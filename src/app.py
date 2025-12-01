import os
import random
from flask import Flask, jsonify, request, render_template

from .db import init_db_from_csv, get_db_connection

# Paths & config
CSV_PATH = os.environ.get("MEGAGYM_CSV_PATH", "data/megaGymDataset.csv")
DB_PATH = os.environ.get("DB_PATH", "data/gymcoach.db")
PORT = int(os.environ.get("PORT", "8080"))

# Create the Flask app and point it to templates/static inside src/
app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize the database when the app starts
init_db_from_csv(DB_PATH, CSV_PATH)

# Map logical group names to BodyPart values in the dataset
GROUP_BODY_PART_MAP = {
    "chest": ["chest"],
    "back": ["back"],
    "biceps": ["biceps"],
    "triceps": ["triceps"],
    "legs": ["legs", "upper legs", "lower legs"],
    "shoulders": ["shoulders", "shoulder"],
    "core": ["abdominals", "abs", "core"],
}


def build_single_group_workout(conn, group_name=None, size: int = 5):
    """
    Build a workout that focuses on a SINGLE muscle group.

    If group_name is None, pick a random one from GROUP_BODY_PART_MAP.
    Returns a dict with group and list of exercises.
    """
    available_groups = list(GROUP_BODY_PART_MAP.keys())

    # Choose group: either user-specified or random
    if group_name:
        group_key = str(group_name).strip().lower()
        if group_key not in GROUP_BODY_PART_MAP:
            group_key = random.choice(available_groups)
    else:
        group_key = random.choice(available_groups)

    target_body_parts = [bp.lower() for bp in GROUP_BODY_PART_MAP[group_key]]

    # Load all exercises once
    rows = conn.execute("SELECT * FROM exercises").fetchall()
    all_exercises = [dict(r) for r in rows]

    # Filter exercises that match the chosen group
    candidates = []
    for ex in all_exercises:
        bp = ex.get("body_part")
        if not bp:
            continue
        if bp.strip().lower() in target_body_parts:
            candidates.append(ex)

    if not candidates:
        # If somehow no matches, fall back to all exercises
        candidates = all_exercises

    # Sample up to `size` exercises
    if len(candidates) <= size:
        chosen = candidates
    else:
        chosen = random.sample(candidates, size)

    workout_exercises = []
    for i, ex in enumerate(chosen, start=1):
        workout_exercises.append({
            "order": i,
            "title": ex.get("title"),
            "body_part": ex.get("body_part"),
            "type": ex.get("type"),
            "equipment": ex.get("equipment"),
            "level": ex.get("level"),
            "sets": 3,
            "reps": "8–12",
        })

    return {
        "group": group_key.capitalize(),
        "exercises": workout_exercises,
    }


# ---------- HTML PAGES ----------

@app.route("/", methods=["GET"])
def home():
    """
    Landing page that introduces you + GymCoach
    and has a button to go to the workout generator.
    """
    return render_template("home.html")


@app.route("/workout", methods=["GET"])
def workout_page():
    """
    Workout generator UI:
      - Single-group workout (Chest day, Back day, etc.)
      - Query params:
          ?group=chest/back/legs/biceps/triceps/shoulders/core
          ?size=number_of_exercises
    """
    group_param = request.args.get("group")
    size_param = request.args.get("size")

    try:
        size = int(size_param) if size_param else 5
    except ValueError:
        size = 5

    conn = get_db_connection(DB_PATH)
    workout = build_single_group_workout(conn, group_name=group_param, size=size)
    conn.close()

    return render_template(
        "index.html",
        workout_name=f"{workout['group']} Focus – GymCoach",
        group=workout["group"],
        exercises=workout["exercises"],
        available_groups=list(GROUP_BODY_PART_MAP.keys()),
        size=size,
    )


# ---------- JSON API ENDPOINTS ----------

@app.route("/api/workout", methods=["GET"])
def workout_api():
    """JSON version of the workout (same logic as /workout)."""
    group_param = request.args.get("group")
    size_param = request.args.get("size")

    try:
        size = int(size_param) if size_param else 5
    except ValueError:
        size = 5

    conn = get_db_connection(DB_PATH)
    workout = build_single_group_workout(conn, group_name=group_param, size=size)
    conn.close()

    return jsonify({
        "status": "ok",
        "workout_name": f"{workout['group']} Focus – GymCoach",
        "group": workout["group"],
        "total_exercises": len(workout["exercises"]),
        "exercises": workout["exercises"],
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/exercises", methods=["GET"])
def list_exercises():
    """Raw list of all exercises (JSON)."""
    conn = get_db_connection(DB_PATH)
    rows = conn.execute("SELECT * FROM exercises").fetchall()
    conn.close()

    items = [dict(row) for row in rows]
    return jsonify({"count": len(items), "exercises": items}), 200


if __name__ == "__main__":
    print(f"Starting GymCoach on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)
