import os
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from app.database import salva_o_aggiorna_gioco, ottieni_profilo_utente

load_dotenv()

@tool
def cerca_sul_web(query: str):
    """
    Usa questo strumento per cercare sul web informazioni in tempo reale su videogiochi,
    prezzi, recensioni, uscite recenti o consigli. Scrivi query di ricerca sensate (es. 'migliori giochi PS5 2026').
    """
    try:
        # Puliamo la query da caratteri strani o apici
        query_pulita = query.replace('"', '').replace("'", "")
        with DDGS() as ddgs:
            risultati = [r for r in ddgs.text(query_pulita, max_results=3)]
            if not risultati:
                return "Nessun risultato specifico trovato sul web. Consiglia i giochi più famosi basandoti sulla tua conoscenza."
            
            testo_risultati = ""
            for r in risultati:
                testo_risultati += f"Titolo: {r['title']}\nContenuto: {r['body']}\n\n"
            return testo_risultati
    except Exception as e:
        # Se DuckDuckGo blocca la richiesta, non crashiamo ma usiamo la conoscenza dell'IA
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

def configuro_agente_videogiochi(user_id: str):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.5,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    cronologia_utente = ottieni_profilo_utente(user_id)
    tools = [cerca_sul_web, aggiorna_preferenze_database]
    
    # Questo prompt dice all'IA di scegliere se usare uno strumento o rispondere direttamente
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "Sei Rufus, un assistente esperto di videogiochi, amichevole e super preparato.\n"
            f"Ecco la cronologia dei giochi dell'utente attuale (ID: {user_id}):\n"
            f"{cronologia_utente}\n\n"
            "REGOLE:\n"
            "1. Se l'utente ti chiede dei consigli o notizie fresche (es. giochi per Play 5 o PC), rispondi usando le tue conoscenze oppure inventa una query di ricerca intelligente.\n"
            "2. Rispondi sempre in modo naturale, dettagliato e in italiano."
        )),
        ("human", "{input}"),
    ])
    
    # Colleghiamo i tool al modello
    llm_con_tools = llm.bind_tools(tools)
    catena = prompt | llm_con_tools
    
    return catena, tools