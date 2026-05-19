@echo off
echo Avvio del progetto Full-Stack in corso...
:: 2. Usa lo stesso trucco per il Backend
start "Backend" cmd /k "cd backend && title Backend && .\venv\Scripts\uvicorn app.main:app --reload"

:: 1. Usa il flag /ti di start per bloccare il titolo del Frontend
start "Frontend" cmd /k "cd frontend && title Frontend && npm run dev"


echo Pronto! Le finestre si sono aperte separatamente.