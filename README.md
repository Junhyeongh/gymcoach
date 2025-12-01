# GymCoach Pro – Single-Group Workout Generator

This project:

- Loads `megaGymDataset.csv` into a SQLite database
- Serves a Flask web UI to generate **single muscle-group workouts**
- Lets you choose:
  - Muscle group (chest, back, legs, biceps, triceps, shoulders, core)
  - Number of exercises

## Setup

1. Place your `megaGymDataset.csv` file into the `data/` folder.

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python3 -m src.app
   ```

4. Visit:

   - HTML UI: http://localhost:8080/
   - JSON API: http://localhost:8080/api/workout
   - Health check: http://localhost:8080/health
