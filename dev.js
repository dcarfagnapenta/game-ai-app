const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Avvio di Ai Gaming App in Modalità Isolata Avanzata...');

const backendCmd = process.platform === 'win32' 
  ? 'venv\\Scripts\\activate && uvicorn app.main:app --reload' 
  : 'source venv/bin/activate && uvicorn app.main:app --reload';

// Avvia il Backend
const backend = spawn(backendCmd, {
  shell: true,
  cwd: path.join(__dirname, 'backend'),
  stdio: 'inherit'
});

// Avvia il Frontend
const frontend = spawn('npm run dev', {
  shell: true,
  cwd: path.join(__dirname, 'frontend'),
  stdio: 'inherit'
});

// Intercetta gli errori di processo per evitare il crash globale dello script
backend.on('error', (err) => {});
frontend.on('error', (err) => {});

// Si attiva SOLO se premi fisicamente CTRL + C nel terminale di VS Code
process.on('SIGINT', () => {
  console.log('\n🛑 Spegnimento totale dei server in corso...');
  try { backend.kill(); } catch (e) {}
  try { frontend.kill(); } catch (e) {}
  process.exit(0);
});