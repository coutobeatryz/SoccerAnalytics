from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

# --- CONFIGURAÇÃO ---
API_KEY = "22d4f974d91b4f5cab1b66e4d580bece"
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = "https://api.football-data.org/v4"
TIMEOUT_SEGUNDOS = 15
COMPETITION_CODE = 'BSA'

PESO_H2H = 0.40
PESO_FASE = 0.35
PESO_TABELA = 0.25

app = Flask(__name__)

def get_standings(competition_code):
    try:
        url = f"{BASE_URL}/competitions/{competition_code}/standings"
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEGUNDOS)
        response.raise_for_status()
        return response.json()['standings'][0]['table']
    except requests.exceptions.RequestException:
        return None

def get_team_info(team_name, standings):
    if not standings: return None
    for team_data in standings:
        team = team_data['team']
        if team_name.lower() in team['name'].lower() or \
           (team.get('shortName') and team_name.lower() in team['shortName'].lower()):
            return {"id": team['id'], "name": team['name'], "crest": team.get('crest'), "position": team_data['position']}
    return None

def get_matches(team_id, params={}):
    try:
        url = f"{BASE_URL}/teams/{team_id}/matches"
        response = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT_SEGUNDOS)
        response.raise_for_status()
        return response.json().get('matches', [])
    except requests.exceptions.RequestException:
        return None

def get_top_scorers(competition_code, limit=5):
    try:
        url = f"{BASE_URL}/competitions/{competition_code}/scorers?limit={limit}"
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEGUNDOS)
        response.raise_for_status()
        scorers_data = response.json().get('scorers', [])
        
        formatted_scorers = []
        for scorer in scorers_data:
            formatted_scorers.append({
                "name": scorer['player']['name'],
                "team": scorer['team']['name'],
                "goals": scorer.get('goals', 0)
            })
        return formatted_scorers
    except requests.exceptions.RequestException:
        return []

def analyze_stats(team_id, matches):
    if not matches:
        return {"jogos_analisados": 0, "gols_marcados": 0, "gols_sofridos": 0, "vitorias": 0, "empates": 0, "derrotas": 0, "taxa_vitoria": 0, "gols_marcados_ht": 0, "gols_sofridos_ht": 0}

    v, e, d, gm, gs, gm_ht, gs_ht = 0, 0, 0, 0, 0, 0, 0
    
    for match in matches:
        score = match.get('score', {})
        full_time = score.get('fullTime', {})
        half_time = score.get('halfTime', {})
        
        home_score, away_score = full_time.get('home'), full_time.get('away')
        home_score_ht, away_score_ht = half_time.get('home'), half_time.get('away')

        if home_score is None or away_score is None: continue

        is_home = match['homeTeam']['id'] == team_id
        
        if is_home:
            gm += home_score; gs += away_score
            if home_score_ht is not None: gm_ht += home_score_ht; gs_ht += away_score_ht
            if home_score > away_score: v += 1
            elif home_score == away_score: e += 1
            else: d += 1
        else: 
            gm += away_score; gs += home_score
            if away_score_ht is not None: gm_ht += away_score_ht; gs_ht += home_score_ht
            if away_score > home_score: v += 1
            elif away_score == home_score: e += 1
            else: d += 1
            
    num_jogos = v + e + d
    return {
        "jogos_analisados": num_jogos,
        "gols_marcados": gm, "gols_sofridos": gs,
        "gols_marcados_ht": gm_ht, "gols_sofridos_ht": gs_ht,
        "vitorias": v, "empates": e, "derrotas": d,
        "taxa_vitoria": (v / num_jogos) if num_jogos > 0 else 0
    }

def run_full_analysis(team1_name, team2_name):
    standings = get_standings(COMPETITION_CODE)
    if not standings: return {"error": "Não foi possível obter a tabela de classificação."}

    team1_info = get_team_info(team1_name, standings)
    team2_info = get_team_info(team2_name, standings)
    if not team1_info or not team2_info: return {"error": "Um ou ambos os times não foram encontrados."}

    h2h_matches = get_matches(team1_info['id'], {'competitors': team2_info['id']})
    t1_last_matches = get_matches(team1_info['id'], {'status': 'FINISHED', 'limit': 5})
    t2_last_matches = get_matches(team2_info['id'], {'status': 'FINISHED', 'limit': 5})
    top_scorers = get_top_scorers(COMPETITION_CODE)

    finished_h2h = [m for m in h2h_matches if m['status'] == 'FINISHED'][-5:]
    t1_stats_h2h = analyze_stats(team1_info['id'], finished_h2h)
    
    num_h2h = t1_stats_h2h.get('jogos_analisados', 0)
    t2_stats_h2h = {
        "vitorias": t1_stats_h2h['derrotas'], "derrotas": t1_stats_h2h['vitorias'],
        "empates": t1_stats_h2h['empates'], "gols_marcados": t1_stats_h2h['gols_sofridos'],
        "gols_sofridos": t1_stats_h2h['gols_marcados'], "gols_marcados_ht": t1_stats_h2h['gols_sofridos_ht'],
        "gols_sofridos_ht": t1_stats_h2h['gols_marcados_ht']
    }

    t1_stats_fase = analyze_stats(team1_info['id'], t1_last_matches)
    t2_stats_fase = analyze_stats(team2_info['id'], t2_last_matches)
    
    fator_h2h_t1 = t1_stats_h2h.get('taxa_vitoria', 0.5)
    fator_h2h_t2 = 1 - fator_h2h_t1
    fator_fase_t1 = t1_stats_fase.get('taxa_vitoria', 0.5)
    fator_fase_t2 = t2_stats_fase.get('taxa_vitoria', 0.5)
    total_times = len(standings)
    fator_tabela_t1 = (total_times - team1_info['position']) / total_times
    fator_tabela_t2 = (total_times - team2_info['position']) / total_times

    power_score_t1 = (fator_h2h_t1 * PESO_H2H) + (fator_fase_t1 * PESO_FASE) + (fator_tabela_t1 * PESO_TABELA)
    power_score_t2 = (fator_h2h_t2 * PESO_H2H) + (fator_fase_t2 * PESO_FASE) + (fator_tabela_t2 * PESO_TABELA)
    
    total_power = power_score_t1 + power_score_t2
    prob_vitoria_t1 = (power_score_t1 / total_power) if total_power > 0 else 0.5
    prob_vitoria_t2 = (power_score_t2 / total_power) if total_power > 0 else 0.5
    
    prob_empate_h2h = (t1_stats_h2h.get('empates', 0) / num_h2h) if num_h2h > 0 else 0.25
    fator_nao_empate = 1 - prob_empate_h2h
    prob_vitoria_t1 *= fator_nao_empate
    prob_vitoria_t2 *= fator_nao_empate

    return {
        "team1": {"name": team1_info['name'], "crest": team1_info['crest'], "position": team1_info['position']},
        "team2": {"name": team2_info['name'], "crest": team2_info['crest'], "position": team2_info['position']},
        "probabilities": {
            "team1_win": round(prob_vitoria_t1 * 100, 1),
            "team2_win": round(prob_vitoria_t2 * 100, 1),
            "draw": round(prob_empate_h2h * 100, 1),
        },
        "stats": {
            "fase_atual": {"team1": t1_stats_fase, "team2": t2_stats_fase},
            "confronto_direto": {"team1": t1_stats_h2h, "team2": t2_stats_h2h}
        },
        "top_scorers": top_scorers
    }

@app.route("/")
def index():
    top_scorers = get_top_scorers(COMPETITION_CODE)
    return render_template('index.html', top_scorers=top_scorers)

@app.route("/analyze")
def analyze():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    if not team1 or not team2:
        return jsonify({"error": "Nomes dos times são obrigatórios."}), 400
    data = run_full_analysis(team1, team2)
    if "error" in data:
        return jsonify(data), 404
    return jsonify(data)
    
if __name__ == "__main__":

    app.run(debug=True)
