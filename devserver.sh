#!/bin/sh
source .venv/bin/activate

# Carrega as variáveis de ambiente do arquivo .env
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

python -u -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
