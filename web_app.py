from flask import Flask, jsonify, request, send_from_directory, session
from rps_core import RPSPlusReferee, GameState
import os

app = Flask(__name__, static_folder="static")
# NOTE: In production, use a secure random key from environment
app.secret_key = os.environ.get("RPS_SECRET", "dev-secret-key")

# In-memory store keyed by session (simple, no DB)
_engine_by_session = {}

def get_engine() -> RPSPlusReferee:
    sid = session.get("sid")
    if not sid:
        sid = os.urandom(16).hex()
        session["sid"] = sid
    if sid not in _engine_by_session:
        _engine_by_session[sid] = RPSPlusReferee()
    return _engine_by_session[sid]

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/state", methods=["GET"])  # get current game state
def api_state():
    eng = get_engine()
    s = eng.state
    return jsonify({
        "current_round": s.current_round,
        "user": {"score": s.user.score, "bomb_used": s.user.bomb_used},
        "bot": {"score": s.bot.score, "bomb_used": s.bot.bomb_used},
        "game_over": s.game_over,
        "winner": s.winner,
        "valid_moves": RPSPlusReferee.VALID_MOVES,
        "max_rounds": RPSPlusReferee.MAX_ROUNDS,
    })

@app.route("/api/move", methods=["POST"])  # submit a move
def api_move():
    eng = get_engine()
    data = request.get_json(force=True, silent=True) or {}
    user_move = str(data.get("move", "")).strip().lower()

    result, message, bot_move = eng.play_turn(user_move)
    s = eng.state
    return jsonify({
        "result": result,
        "message": message,
        "bot_move": bot_move,
        "state": {
            "current_round": s.current_round,
            "user": {"score": s.user.score, "bomb_used": s.user.bomb_used},
            "bot": {"score": s.bot.score, "bomb_used": s.bot.bomb_used},
            "game_over": s.game_over,
            "winner": s.winner,
        }
    })

@app.route("/api/reset", methods=["POST"])  # start a new game
def api_reset():
    eng = get_engine()
    _sid = session.get("sid")
    # Replace engine with fresh state
    from rps_core import GameState
    _engine_by_session[_sid] = RPSPlusReferee(GameState())
    return jsonify({"ok": True})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
