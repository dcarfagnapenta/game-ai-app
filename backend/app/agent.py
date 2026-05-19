import os
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from app.database import salva_o_aggiorna_gioco, ottieni_profilo_utente

load_dotenv()

# Recupera la chiave API globale
CHIAVE_GROQ = os.environ.get("GROQ_API_KEY")

# ==========================================
# 1. DEFINIZIONE DEI TOOL (STRUMENTI)
# ==========================================

@tool
def cerca_sul_web(query: str):
    """
    Usa questo strumento per cercare sul web informazioni in tempo reale su videogiochi,
    prezzi, recensioni, uscite recenti o consigli. Scrivi query di ricerca sensate.
    """
    try:
        query_pulita = query.replace('"', '').replace("'", "")
        with DDGS() as ddgs:
            risultati = [r for r in ddgs.text(query_pulita, max_results=3)]
            if not risultati:
                return "Nessun risultato specifico trovato sul web."
            
            testo_risultati = ""
            for r in risultati:
                testo_risultati += f"Titolo: {r['title']}\nContenuto: {r['body']}\n\n"
            return testo_risultati
    except Exception as e:
        return "Errore temporaneo di connessione al web. Usa la tua conoscenza interna dei giochi per rispondere."

@tool
def aggiorna_preferenze_database(user_id: str, titolo_gioco: str, completato: bool = None, piaciuto: str = None):
    """
    Usa questo strumento per aggiornare il database quando l'utente rivela se ha giocato, 
    finito o abbandonato un gioco.
    """
    try:
        comp_int = 1 if completato is True else (0 if completato is False else None)
        salva_o_aggiorna_gioco(user_id, titolo_gioco, completato=comp_int, voto=piaciuto)
        return f"Database aggiornato per il gioco {titolo_gioco}."
    except:
        return "Impossibile aggiornare il database al momento."


# ==========================================
# 2. FUNZIONE PRINCIPALE DI CONFIGURAZIONE
# ==========================================

def configuro_agente_videogiochi(user_id: str):
    # Modello 8B: stabile, leggero e con limiti di token altissimi per evitare l'errore 429
    llm = ChatGroq(
        model="llama-3.1-8b-instant", 
        temperature=0.5,
        groq_api_key=CHIAVE_GROQ
    )
    
    # Recupera i ricordi a lungo termine dal DB
    cronologia_utente_db = ottieni_profilo_utente(user_id)
    tools = [cerca_sul_web, aggiorna_preferenze_database]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Sei Pixel, un gamer esperto, appassionato e super diretto. Parli come un amico su Discord. "
            "Evita risposte robotiche, presentazioni fisse da assistente o elenchi da enciclopedia.\n\n"
            f"Ecco il profilo storico dei giochi preferiti dell'utente (dal DB): {cronologia_utente_db}\n\n"
            "REGOLE DI CONVERSAZIONE:\n"
            "1. Sii conciso e vai dritto al punto.\n"
            "2. Guarda sempre la cronologia della chat precedente! Se l'utente ti fa una domanda legata al messaggio prima (es. 'fa paura?'), "
            "tu sai che si riferisce all'ultimo gioco di cui avete appena parlato. Mantieni il contesto vivo!"
        )),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    
    llm_con_tools = llm.bind_tools(tools)
    catena_base = prompt | llm_con_tools
    
    # Gestione della memoria ottimizzata (Sliding Window a 6 messaggi)
    def prendi_cronologia_chat(session_id: str):
        storia_completa = SQLChatMessageHistory(
            session_id=f"chat_{session_id}",
            connection="sqlite:///database.db"
        )
        
        tutti_i_messaggi = storia_completa.messages
        
        # Se superiamo i 6 messaggi (3 botta e risposta), creiamo una finestra scorrevole
        if len(tutti_i_messaggi) > 6:
            messaggi_filtrati = tutti_i_messaggi[-6:]
            
            storia_ottimizzata = SQLChatMessageHistory(
                session_id=f"temp_{session_id}", 
                connection="sqlite:///database.db"
            )
            storia_ottimizzata.clear()
            
            for msg in messaggi_filtrati:
                storia_ottimizzata.add_message(msg)
                
            return storia_ottimizzata
            
        return storia_completa
    
    catena_con_memoria = RunnableWithMessageHistory(
        catena_base,
        prendi_cronologia_chat,
        input_messages_key="input",
        history_messages_key="history"
    )
    
    return catena_con_memoria, tools