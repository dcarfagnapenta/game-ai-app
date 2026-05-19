import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent import configuro_agente_videogiochi
from langchain_groq import ChatGroq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessaggioUtente(BaseModel):
    user_id: str
    text: str

@app.post("/chat")
async def chat(request: MessaggioUtente):
    try:
        # 1. Recupera la catena (con memoria ottimizzata) e la lista dei tools
        catena, tools = configuro_agente_videogiochi(request.user_id)
        
        # 2. Invoca il modello passando l'input e la configurazione della sessione per il DB
        risposta_modello = catena.invoke(
            {"input": request.text},
            config={"configurable": {"session_id": request.user_id}}
        )
        
        # 3. Controlla se il modello vuole usare un Tool (es. ricerca web)
        if hasattr(risposta_modello, "tool_calls") and risposta_modello.tool_calls:
            mapping_tools = {t.name: t for t in tools}
            
            for tool_call in risposta_modello.tool_calls:
                nome_tool = tool_call["name"]
                argomenti = tool_call["args"]
                
                risultato_tool = mapping_tools[nome_tool].invoke(argomenti)
                
                # Prompt per la risposta finale testuale pulita, sicura e coerente
                prompt_riassunto = (
                    f"L'utente ha chiesto: '{request.text}'.\n"
                    f"Il tool '{nome_tool}' ha restituito questi dati:\n{risultato_tool}\n\n"
                    "Genera una risposta finale esaustiva, amichevole e in italiano. "
                    "Se i dati del tool indicano che non ci sono risultati o sono scarsi, non dire che c'è stato un errore! "
                    "Usa le tue conoscenze personali per dare una risposta eccellente, sicura e immediata."
                )
                
                # Usiamo l'8B anche qui per garantire stabilità assoluta
                llm_finale = ChatGroq(
                    model="llama-3.1-8b-instant", 
                    groq_api_key=os.getenv("GROQ_API_KEY"), 
                    temperature=0.6
                )
                
                risposta_finale = llm_finale.invoke(prompt_riassunto)
                
                return {"risposta": risposta_finale.content}
        
        # 4. Risposta diretta senza tool
        return {"risposta": risposta_modello.content}

    except Exception as e:
        print(f"[-] Errore server: {str(e)}")
        return {"risposta": f"Pixel ha avuto un piccolo glitch: {str(e)}"}