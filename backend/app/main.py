# =========================================================
# MAIN.PY
# =========================================================

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage
)

from app.agent import (
    configuro_agente_videogiochi
)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI()


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST
# =========================================================

class MessaggioUtente(BaseModel):

    user_id: str
    text: str


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
async def chat(request: MessaggioUtente):

    try:

        # =====================================================
        # CONFIG AGENTE
        # =====================================================

        llm, memoria, tools, system_prompt = (
            configuro_agente_videogiochi(
                request.user_id
            )
        )

        # =====================================================
        # MESSAGGI CHAT
        # =====================================================

        messaggi = []

        # SYSTEM PROMPT

        messaggi.append(

            SystemMessage(
                content=system_prompt
            )
        )

        # MEMORIA CHAT

        messaggi.extend(
            memoria.messages[-6:]
        )

        # MESSAGGIO UTENTE

        messaggi.append(

            HumanMessage(
                content=request.text
            )
        )

        # =====================================================
        # TOOL BINDING
        # =====================================================

        llm_tools = llm.bind_tools(
            list(tools.values())
        )

        # =====================================================
        # RISPOSTA MODELLO
        # =====================================================

        risposta = llm_tools.invoke(
            messaggi
        )

        # =====================================================
        # TOOL CALL
        # =====================================================

        if risposta.tool_calls:

            messaggi.append(risposta)

            for tool_call in risposta.tool_calls:

                nome_tool = tool_call["name"]

                args = tool_call["args"]

                # AGGIUNGE USER_ID AUTOMATICO

                if nome_tool == "aggiorna_preferenze_database":

                    args["user_id"] = request.user_id

                # ESEGUE TOOL

                risultato = tools[
                    nome_tool
                ].invoke(args)

                # AGGIUNGE RISULTATO TOOL

                messaggi.append(

                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(risultato)
                    )
                )

            # RISPOSTA FINALE

            risposta_finale = llm.invoke(
                messaggi
            )

            testo_finale = risposta_finale.content

        else:

            testo_finale = risposta.content

        # =====================================================
        # FILTRO FRASI CHATGPT
        # =====================================================

        frasi_vietate = [

            "grafica incredibile",

            "gameplay emozionante",

            "esperienza immersiva"
        ]

        for frase in frasi_vietate:

            testo_finale = testo_finale.replace(
                frase,
                ""
            )

        # =====================================================
        # PULIZIA TOOL VISIBILI
        # =====================================================

        if "<function=" in testo_finale:

            testo_finale = (
                testo_finale
                .split("<function=")[0]
                .strip()
            )

        if "tool_calls" in testo_finale:

            testo_finale = (
                testo_finale
                .replace("tool_calls", "")
            )

        # =====================================================
        # SALVA MEMORIA
        # =====================================================

        memoria.add_message(

            HumanMessage(
                content=request.text
            )
        )

        memoria.add_message(

            AIMessage(
                content=testo_finale
            )
        )

        # =====================================================
        # RISPOSTA API
        # =====================================================

        return {

            "risposta": testo_finale
        }

    except Exception as e:

        print(
            "ERRORE SERVER:",
            str(e)
        )

        return {

            "risposta":
                f"Pixel è crashato 💀 ({str(e)})"
        }