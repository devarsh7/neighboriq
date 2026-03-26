# NeighborIQ

A real estate intelligence tool that takes a neighborhood name and gives you an AI-generated market analysis in seconds — confidence score, price trends, risk flags, and a chat interface to ask follow-up questions.

Built in as a prototype. The idea was simple: instead of spending hours reading listings and market reports, what if an AI agent did all of that and handed you a clear verdict?

---

## What it does

You type in a neighborhood (e.g. "Leslieville, Toronto") and it runs a 5-step agent pipeline:

1. Pulls neighborhood data — prices, days on market, rental yield, walkability
2. Computes market signals — demand score, supply tightness, price momentum
3. Calculates a confidence score (0–100) with a breakdown of what's driving it
4. Generates a written market report using Claude
5. Lets you ask follow-up questions in a chat interface, with full context

There's also a compare mode where you can put up to 3 neighborhoods side by side.

<img width="1528" height="731" alt="image" src="https://github.com/user-attachments/assets/056e4226-521c-4537-900b-23f85c4d309e" />


<img width="1348" height="750" alt="image" src="https://github.com/user-attachments/assets/14b67c0e-f949-4a8b-bbdb-8c8821ebb783" />


<img width="1411" height="696" alt="image" src="https://github.com/user-attachments/assets/6d0dccd3-9110-4283-94e3-437e62eea5c8" />


<img width="1373" height="768" alt="image" src="https://github.com/user-attachments/assets/df1fd94a-7e02-4b2a-aa34-ca313e617d70" />





---

## Stack

- **LangGraph** — orchestrates the agent pipeline
- **Claude** (Anthropic) — writes the report and answers questions
- **FastAPI** — backend API
- **Streamlit** — frontend
- **Brave Search** — optional, for live news signals

---

## Setup

```bash
git clone https://github.com/devarsh7/neighboriq.git
cd neighboriq

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

**Run the backend:**
```bash
set PYTHONPATH=C:\path\to\neighboriq
uvicorn backend.main:app --reload --port 8000
```

**Run the frontend** (new terminal):
```bash
set PYTHONPATH=C:\path\to\neighboriq
streamlit run frontend/app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Preloaded neighborhoods

The Annex, Leslieville, Liberty Village, Queen West, Scarborough (Toronto) · Brooklyn (New York) · Wynwood (Miami) · Mission District (San Francisco)

Any other neighborhood will get a synthetic baseline estimate.

---

## API

```
GET  /health
POST /analyze          {"neighborhood": "Leslieville", "city": "Toronto"}
POST /analyze/compare  {"neighborhoods": [...]}
POST /chat
GET  /docs             Swagger UI
```
