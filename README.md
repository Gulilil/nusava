# nusava
Social media bot in Instagram based on LLM and Data Mining

## Library
#### Python Dependencies
```bash
pip install -r requirements.txt
```

## For frontend
```bash
# Setup
cd src/frontend-v2
npm install

# Run Client
npm run dev
```

## For backend
```bash
# Setup
python src/backend/manage.py makemigrations bot
python src/backend/manage.py migrate
# Run Server
python src/backend/manage.py runserver
```

## For LLM 
```bash
# Run LLM server
python src/llm/src/main.py
```
