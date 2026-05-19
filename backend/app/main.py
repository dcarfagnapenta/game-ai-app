from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agent import configuro_agente_videogiochi, CHIAVE_GROQ

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
        # 1. Recupera la catena (ora provvista di memoria strutturata)
        catena, tools = configuro_agente_videogiochi(request.user_id)
        
        # 2. Invochiamo passando la sessione dell'utente nel config
        risposta_modello = catena.invoke(
            {"input": request.text},
            config={"configurable": {"session_id": request.user_id}}
        )
        
        # 3. Gestione Tool (Ricerca Web)
        if hasattr(risposta_modello, "tool_calls") and risposta_modello.tool_calls:
            mapping_tools = {t.name: t for t in tools}
            
            for tool_call in risposta_modello.tool_calls:
                nome_tool = tool_call["name"]
                argomenti = tool_call["args"]
                
                risultato_tool = mapping_tools[nome_tool].invoke(argomenti)
                
                prompt_riassunto = (
                    f"L'utente ha chiesto: '{request.text}'.\n"
                    f"Il tool '{nome_tool}' ha restituito questi dati:\n{risultato_tool}\n\n"
                    "Genera una risposta finale nel ruolo di Pixel: amichevole, da vero gamer, in italiano. "
                    "Usa i dati appena trovati uniti alle tue conoscenze per dare una risposta eccellente."
                )
                
                from langchain_groq import ChatGroq
                # Usiamo la chiave blindata importata direttamente da agent.py
                llm_finale = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=CHIAVE_GROQ, temperature=0.6)
                
                risposta_finale = llm_finale.invoke(prompt_riassunto)
                
                return {"risposta": risposta_finale.content}
        
        # 4. Risposta diretta senza tool
        return {"risposta": risposta_modello.content}

    except Exception as e:
        print(f"[-] Errore server: {str(e)}")
        return {"risposta": f"Pixel ha avuto un piccolo glitch: {str(e)}"}