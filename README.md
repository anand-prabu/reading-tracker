# Reading Tracker App (PostgreSQL)

## Build stack
- Streamlit
- PostgreSQL
- SQLAlchemy
- Plotly
- Google OIDC or another free OIDC provider

## Step-by-step on Mac + VS Code + GitHub

### 1) Install tools
- Install Python 3.11+.
- Install VS Code.
- Install Git.
- Open Terminal and verify:
```bash
python3 --version
git --version
```

### 2) Create project folder
```bash
mkdir reading_tracker
cd reading_tracker
```
Copy the generated files into this folder.

### 3) Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Create PostgreSQL database
Use one of these free options:
- Supabase Postgres
- Neon Postgres

Create a database and note:
- host
- database name
- username
- password

### 5) Add secrets
Create `.streamlit/secrets.toml` with your auth and database values.

Example:
```toml
[database]
host = "host name"
port = 5432
database = "postgres"
username = "username"
password = "YOUR_ACTUAL_SUPABASE_PASSWORD"

[auth]
redirect_uri = "your-app-name.streamlit.app"
cookie_secret = "your-random-32-char-string-same-as-local"

[google]
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"

[app]
admin_emails = ["username@gmail.com"]
```

### 6) Run locally
```bash
streamlit run Home.py
```

### 7) Promote yourself to admin
After your first login, update your user row in PostgreSQL:
```sql
update users set role='admin' where email='your-email@example.com';
```

### 8) Push to GitHub
```bash
git init
git add .
git commit -m "Initial reading tracker app"
git branch -M main
git remote add origin https://github.com/yourname/reading-tracker.git
git push -u origin main
```

### 9) Deploy on Streamlit Community Cloud
1. Go to Streamlit Community Cloud.
2. Connect GitHub.
3. Choose your repository.
4. Set `Home.py` as the entry file.
5. Paste the same secrets into the app Secrets page.
6. Deploy.

### 10) Recommended next edits
- Add a recommendation page.
- Add CSV import/export for users and books.
- Add master-library similarity scoring.
- Add book cover images.
