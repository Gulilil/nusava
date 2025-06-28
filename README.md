# nusava
Social media bot in Instagram based on LLM and Data Mining

## Library
#### Python Dependencies
```bash

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
# Install libraries
pip install -r src/backend/requirements.txt

# Setup
python src/backend/manage.py makemigrations bot
python src/backend/manage.py migrate
# Run Server
python src/backend/manage.py runserver
```

## For LLM 
```bash
# Install libraries
pip install -r src/llm/requirements.txt

# Run LLM server
python src/llm/main.py
```
