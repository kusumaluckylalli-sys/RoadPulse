RoadPulse - cleaned final project

1. Open this folder in VS Code.
2. Open Terminal -> New Terminal.
3. Run: pip install -r requirements.txt
4. Run once if you want a fresh database: python reset_database.py
5. Run: streamlit run app.py
6. Open http://localhost:8501

Important fixes in this version:
- Light readable theme.
- No raw HTML code in Home page cards.
- Government Portal is visible on Home and sidebar.
- Tracking uses Report ID only, not phone number.
- Government email domain check supports gov.in and nic.in by default.
- Existing old SQLite databases are migrated automatically.
- AI remains optional; app works without models/best.pt.
