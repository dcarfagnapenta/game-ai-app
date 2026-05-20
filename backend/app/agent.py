# =========================================================
# agent.py
# =========================================================

import os

from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_groq import ChatGroq

from langchain_community.chat_message_histories import (
    SQLChatMessageHistory
)

from duckduckgo_search import DDGS

from app.database import (
    salva_o_aggiorna_gioco,
    ottieni_profilo_utente
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================================================
# TOOL WEB
# =========================================================

@tool
def cerca_sul_web(query: str) -> str:
    """
    Cerca informazioni RECENTI sui videogiochi.

    Usare SOLO per:
    - news
    - prezzi
    - patch
    - update
    - date uscita
    """

    try:

        with DDGS() as ddgs:

            risultati = list(
                ddgs.text(query, max_results=2)
            )

        if not risultati:
            return "Nessun risultato trovato."

        testo = ""

        for r in risultati:

            titolo = r.get("title", "")
            body = r.get("body", "")

            testo += (
                f"{titolo}\n"
                f"{body}\n\n"
            )

        return testo

    except Exception as e:

        return f"Errore ricerca web: {str(e)}"


# =========================================================
# TOOL DATABASE
# =========================================================

@tool
def aggiorna_preferenze_database(
    user_id: str,
    titolo_gioco: str,
    completato: bool = None,
    voto: str = None
) -> str:
    """
    Salva preferenze gaming utente.
    """

    try:

        completato_int = None

        if completato is True:
            completato_int = 1

        elif completato is False:
            completato_int = 0

        salva_o_aggiorna_gioco(
            user_id=user_id,
            titolo_gioco=titolo_gioco,
            completato=completato_int,
            voto=voto
        )

        return f"Preferenze salvate per {titolo_gioco}"

    except Exception as e:

        return f"Errore database: {str(e)}"


# =========================================================
# MEMORIA CHAT
# =========================================================

def get_memoria(user_id: str):

    return SQLChatMessageHistory(
        session_id=f"chat_{user_id}",
        connection="sqlite:///database.db"
    )


# =========================================================
# MODELLO
# =========================================================

def get_llm():

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.15,
        timeout=18,
        max_retries=2,
        max_tokens=190,
        groq_api_key=GROQ_API_KEY
    )


# =========================================================
# CONFIG AGENTE
# =========================================================

def configuro_agente_videogiochi(user_id: str):

    llm = get_llm()

    memoria = get_memoria(user_id)

    profilo_utente = ottieni_profilo_utente(user_id)

    tools = {
        "cerca_sul_web": cerca_sul_web,
        "aggiorna_preferenze_database":
            aggiorna_preferenze_database
    }

    system_prompt = f"""
Sei Pixel.

Un gamer esperto che parla come un amico su Discord.

Tono:
- naturale
- diretto
- rilassato
- competente

NON sembrare ChatGPT.

PROFILO UTENTE:
{profilo_utente}

REGOLE:

Ricorda:
- giochi amati
- giochi odiati
- giochi completati

Se l'utente parla delle sue preferenze:
usa aggiorna_preferenze_database.

Usa cerca_sul_web SOLO per:
- news
- prezzi
- patch
- date uscita

NON usarlo per domande gaming normali.

NON inventare informazioni false.

Se conosci pochi esempi corretti:
- fermati
- non inventare altri giochi
- non allargare il significato della domanda

Meglio pochi esempi accurati
che tanti esempi sbagliati.

Se parli di ambientazioni:
- fai attenzione alla città precisa
- non confondere sequel o capitoli diversi
- meglio dire "non ricordo con certezza"
che inventare dettagli sbagliati

Se non sei sicuro:
- dichiaralo
- ragiona insieme all'utente

Se l'utente chiede:
"altri"

non sentirti obbligato
a trovare nuovi esempi a tutti i costi.

Puoi anche dire:
- che gli esempi famosi finiscono lì
- che ci sono pochi giochi davvero noti
- che altri casi sono marginali

Quando consigli giochi:
- pochi giochi
- niente liste infinite
- evita giochi fuori piattaforma
- rispetta il genere richiesto

Per gli shooter:
- principalmente FPS/TPS

Parla come un gamer reale.

Evita frasi tipo:
- grafica incredibile
- gameplay emozionante
- esperienza immersiva

NON mostrare:
- tool_calls
- json
- codice
- function calls
"""

    return llm, memoria, tools, system_prompt