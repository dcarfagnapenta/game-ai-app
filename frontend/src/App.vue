<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500 selection:text-black">
    <div v-if="!inChat" class="flex flex-col items-center justify-center min-h-screen px-6 text-center animate-fade-in">
      <div class="mb-6 p-4 bg-emerald-500/10 rounded-full border border-emerald-500/20">
        <i class="fa-solid fa-robot text-5xl text-emerald-500"></i>
      </div>
      <h1 class="text-6xl md:text-8xl font-bold mb-4 tracking-tighter">
        RUFUS <span class="text-emerald-500">GAMING</span>
      </h1>
      <p class="text-xl md:text-2xl text-slate-400 max-w-2xl mb-12 font-light">
        Il tuo assistente personale che ricorda i tuoi progressi, cerca le ultime novità e ti guida nel mondo del gaming.
      </p>
      <button 
        @click="inChat = true" 
        class="group relative px-10 py-4 bg-emerald-500 text-black font-bold rounded-xl overflow-hidden transition-all hover:scale-105 active:scale-95"
      >
        <span class="relative z-10 flex items-center gap-2">
          ENTRA IN CHAT <i class="fa-solid fa-arrow-right group-hover:translate-x-1 transition-transform"></i>
        </span>
        <div class="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity"></div>
      </button>
    </div>

    <div v-else class="flex flex-col h-screen bg-black animate-slide-up">
      <header class="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center text-black">
            <i class="fa-solid fa-headset"></i>
          </div>
          <div>
            <h2 class="font-bold text-lg leading-tight">RUFUS GPT</h2>
            <p class="text-xs text-emerald-500 flex items-center gap-1">
              <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span> ONLINE
            </p>
          </div>
        </div>
        <button @click="inChat = false" class="text-slate-400 hover:text-white transition-colors">
          <i class="fa-solid fa-xmark text-2xl"></i>
        </button>
      </header>

      <main class="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide" id="chat-container">
        <div v-for="(msg, index) in messages" :key="index" 
          :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
        >
          <div :class="[
            'max-w-[80%] px-5 py-3 rounded-2xl text-lg shadow-xl',
            msg.role === 'user' 
              ? 'bg-emerald-600 text-white rounded-tr-none' 
              : 'bg-slate-800 text-slate-100 rounded-tl-none border border-slate-700'
          ]">
            {{ msg.text }}
          </div>
        </div>
        <div v-if="loading" class="flex justify-start">
          <div class="bg-slate-800 px-5 py-3 rounded-2xl rounded-tl-none border border-slate-700 flex gap-2">
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          </div>
        </div>
      </main>

      <footer class="p-6 bg-slate-900/80 border-t border-slate-800">
        <form @submit.prevent="sendMessage" class="max-w-4xl mx-auto flex gap-4">
          <input 
            v-model="userInput"
            type="text" 
            placeholder="Scrivi a Rufus..." 
            class="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-6 py-4 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
            :disabled="loading"
          />
          <button 
            type="submit"
            :disabled="loading || !userInput.trim()"
            class="bg-emerald-500 text-black w-14 h-14 rounded-xl flex items-center justify-center hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <i class="fa-solid fa-paper-plane text-xl"></i>
          </button>
        </form>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const inChat = ref(false);
const userInput = ref('');
const loading = ref(false);
const messages = ref([
  { role: 'ai', text: 'Ciao! Sono Rufus. Di cosa vogliamo parlare oggi?' }
]);

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return;

  const text = userInput.value;
  messages.value.push({ role: 'user', text });
  userInput.value = '';
  loading.value = true;

  scrollToBottom();

  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: 'anon_user', // Cambieremo questo con l'ID vero in futuro
        text: text
      })
    });

    const data = await response.json();
    messages.value.push({ role: 'ai', text: data.risposta || 'Errore di risposta' });
  } catch (error) {
    messages.value.push({ role: 'ai', text: 'Scusa, Rufus è offline al momento.' });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    const container = document.getElementById('chat-container');
    if (container) container.scrollTop = container.scrollHeight;
  });
};
</script>

<style>
.animate-fade-in { animation: fadeIn 0.8s ease-out; }
.animate-slide-up { animation: slideUp 0.4s ease-out; }
.scrollbar-hide::-webkit-scrollbar { display: none; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}


@keyframes slideUp {
  from { opacity: 0; transform: translateY(100vh); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

Spero che questo design ti piaccia! Fammi sapere se vuoi modificare qualche colore o aggiungere altre funzionalità alla Home.