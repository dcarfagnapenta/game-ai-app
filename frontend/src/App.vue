<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo-area">
        <svg class="assistant-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <path d="M 20,50 A 30,30 0 0,1 80,50" fill="none" stroke="#00ff9d" stroke-width="6" stroke-linecap="round"/>
          <circle cx="50" cy="53" r="25" fill="#1a1a2e" stroke="#00ff9d" stroke-width="4" />
          <circle cx="42" cy="48" r="3" fill="#00ff9d" />
          <circle cx="58" cy="48" r="3" fill="#00ff9d" />
          <path d="M 40,58 Q 50,66 60,58" fill="none" stroke="#00ff9d" stroke-width="3" stroke-linecap="round" />
          <rect x="13" y="42" width="10" height="22" rx="4" fill="#00ff9d" />
          <rect x="77" y="42" width="10" height="22" rx="4" fill="#00ff9d" />
        </svg>
        <div class="title-text">
          <h1>PIXEL </h1>
          <span class="status-badge">
            <span class="pulse-dot"></span> ONLINE
          </span>
        </div>
      </div>
    </header>

    <main class="chat-space" ref="chatSpace">
      <div v-if="messages.length === 0" class="welcome-screen">
        <p>Ciao! Sono <strong>Pixel</strong>, il tuo compagno di gioco intelligente. Di quali videogiochi vogliamo parlare oggi?</p>
      </div>
      
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        :class="['message-wrapper', msg.sender]"
      >
        <div class="message-bubble">
          {{ msg.text }}
        </div>
      </div>

      <div v-if="caricamento" class="message-wrapper assistant">
        <div class="message-bubble spinner-bubble">
          <div class="typing-spinner">
            <div class="bounce1"></div>
            <div class="bounce2"></div>
            <div class="bounce3"></div>
          </div>
        </div>
      </div>
    </main>

    <footer class="input-area">
      <form @submit.prevent="inviaMessaggio" class="input-form">
        <input 
          v-model="nuovoMessaggio" 
          type="text" 
          placeholder="Chiedi a Pixel di un gioco, consigli o novità..." 
          :disabled="caricamento"
        />
        <button type="submit" :disabled="caricamento || !nuovoMessaggio.trim()">
          Invia
        </button>
      </form>
    </footer>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const messages = ref([])
const nuovoMessaggio = ref('')
const caricamento = ref(false)
const chatSpace = ref(null)

// Usiamo un ID utente fisso per i tuoi test (può essere qualunque stringa)
const USER_ID = "player_uno"

const scorrimentoInBasso = async () => {
  await nextTick()
  if (chatSpace.value) {
    chatSpace.value.scrollTop = chatSpace.value.scrollHeight
  }
}

const inviaMessaggio = async () => {
  if (!nuovoMessaggio.value.trim() || caricamento.value) return

  const testoUtente = nuovoMessaggio.value
  messages.value.push({ sender: 'user', text: testoUtente })
  nuovoMessaggio.value = ''
  caricamento.value = true // Attiva lo spinner
  await scorrimentoInBasso()

  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: USER_ID,
        text: testoUtente
      })
    })

    const data = await response.json()
    messages.value.push({ sender: 'assistant', text: data.risposta })
  } catch (error) {
    console.error(error)
    messages.value.push({ sender: 'assistant', text: 'Scusa, ho riscontrato un problema di connessione.' })
  } finally {
    caricamento.value = false // Spegne lo spinner
    await scorrimentoInBasso()
  }
}
</script>

<style scoped>
/* Reset e Stile Base del Contenitore (Tema Dark/Cyberpunk) */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #0d0d1a;
  color: #e2e8f0;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* Header elegante con effetto sfumato */
.app-header {
  background: linear-gradient(135deg, #161630 0%, #0d0d1a 100%);
  padding: 15px 25px;
  border-bottom: 2px solid #1f1f42;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 15px;
}

.assistant-logo {
  width: 50px;
  height: 50px;
  filter: drop-shadow(0 0 8px rgba(0, 255, 157, 0.5));
}

.title-text h1 {
  margin: 0;
  font-size: 1.4rem;
  letter-spacing: 2px;
  color: #00ff9d;
  text-shadow: 0 0 10px rgba(0, 255, 157, 0.3);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #a0aec0;
  font-weight: bold;
  margin-top: 2px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: #00ff9d;
  border-radius: 50%;
  box-shadow: 0 0 8px #00ff9d;
  animation: pulse 2s infinite;
}

/* Area Chat dei Messaggi */
.chat-space {
  flex: 1;
  overflow-y: auto;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-image: radial-gradient(circle at top, #14142b 0%, #0d0d1a 100%);
}

.welcome-screen {
  text-align: center;
  margin: auto;
  max-width: 500px;
  color: #a0aec0;
  font-size: 1.1rem;
  line-height: 1.6;
}

.welcome-screen strong {
  color: #00ff9d;
}

/* Bolle dei Messaggi */
.message-wrapper {
  display: flex;
  width: 100%;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 14px 18px;
  border-radius: 18px;
  font-size: 0.95rem;
  line-height: 1.5;
  white-space: pre-wrap;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user .message-bubble {
  background: linear-gradient(135deg, #0077ff 0%, #0055cc 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .message-bubble {
  background-color: #1f1f42;
  color: #e2e8f0;
  border-bottom-left-radius: 4px;
  border: 1px solid #2d2d5c;
}

/* Area dello Spinner */
.spinner-bubble {
  padding: 12px 20px !important;
  background-color: #1f1f42 !important;
}

.typing-spinner {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 20px;
}

.typing-spinner > div {
  width: 8px;
  height: 8px;
  background-color: #00ff9d;
  border-radius: 50%;
  display: inline-block;
  animation: sk-bouncedelay 1.4s infinite ease-in-out both;
  box-shadow: 0 0 4px #00ff9d;
}

.typing-spinner .bounce1 { animation-delay: -0.32s; }
.typing-spinner .bounce2 { animation-delay: -0.16s; }

/* Barra Input e Bottone */
.input-area {
  padding: 20px 25px;
  background-color: #111126;
  border-top: 2px solid #1f1f42;
}

.input-form {
  display: flex;
  gap: 15px;
  max-width: 1000px;
  margin: 0 auto;
}

input {
  flex: 1;
  background-color: #161630;
  border: 2px solid #2d2d5c;
  border-radius: 12px;
  padding: 14px 20px;
  color: white;
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

input:focus {
  border-color: #00ff9d;
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.2);
}

button {
  background: linear-gradient(135deg, #00ff9d 0%, #00cc7e 100%);
  color: #0d0d1a;
  border: none;
  border-radius: 12px;
  padding: 0 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 255, 157, 0.3);
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 255, 157, 0.5);
}

button:disabled {
  background: #2d2d4e;
  color: #718096;
  cursor: not-allowed;
  box-shadow: none;
}

/* Animazioni */
@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.5; }
}

@keyframes sk-bouncedelay {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>