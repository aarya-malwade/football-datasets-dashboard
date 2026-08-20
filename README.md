# ⚽ Premier League Player Stats Dashboard

An interactive Streamlit dashboard for exploring the 2020-21 Premier League
player statistics dataset (571 players, 20 clubs, 59 stat columns covering
attacking, passing, defending, and goalkeeping metrics).

## Features

- **Sidebar filters** — club, position, nationality, age range, minimum
  appearances, and player name search
- **Overview tab** — goals by club, position breakdown, age distribution,
  top nationalities
- **Leaderboards tab** — rank all players by any numeric stat (goals,
  assists, tackles, passes, etc.) with a bar chart and table
- **Player Comparison tab** — radar chart comparing up to 5 players across
  chosen metrics
- **Data Explorer tab** — browse the filtered table and download it as CSV

## Files

| File               | Purpose                          |
|--------------------|-----------------------------------|
| `app.py`           | The Streamlit dashboard           |
| `players.csv`      | The dataset                       |
| `requirements.txt` | Python dependencies                |

## Setup

1. Make sure `app.py`, `players.csv`, and `requirements.txt` are in the same
   folder.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
streamlit run app.py
```

This opens the dashboard in your browser at `http://localhost:8501`.

## Using a different CSV path

If your data file lives somewhere else or is named differently, update the
`DATA_PATH` variable near the top of `app.py`:

```python
DATA_PATH = "players.csv"  # change to your file's path
```

## Deploying

The app is ready to deploy as-is on [Streamlit Community Cloud](https://streamlit.io/cloud):
push `app.py`, `players.csv`, and `requirements.txt` to a GitHub repo, then
point Streamlit Cloud at `app.py`.

## Notes on the data

Many columns are position-specific and will contain missing values by
design — for example, goalkeeping stats (saves, catches, punches) are only
populated for goalkeepers, and outfield attacking stats are largely empty
for players who never took a shot. The dashboard filters and charts handle
these gaps gracefully (`NaN` values are dropped or ignored where relevant).
