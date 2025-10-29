
# 2. Enhanced style.css with better UI
style_css = ''':root {
  --bg: #0f1724;
  --card: #0b1220;
  --accent: #10b981;
  --accent-hover: #059669;
  --danger: #ef4444;
  --muted: #94a3b8;
  --border: rgba(255,255,255,0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
  background: linear-gradient(180deg, var(--bg), #051023);
  color: #e6eef6;
  min-height: 100vh;
  line-height: 1.6;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  border: 1px solid var(--border);
}

header h1 {
  font-size: 2em;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

#status {
  font-size: 0.9em;
  color: var(--muted);
}

#onlineCount {
  font-size: 1em;
  color: var(--accent);
  font-weight: 600;
}

#controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

#lobby, #onlinePlayersList {
  flex: 1;
  min-width: 280px;
  background: rgba(255,255,255,0.03);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border);
}

#lobby h3, #onlinePlayersList h3 {
  margin: 0 0 15px 0;
  color: var(--accent);
}

#lobby input {
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(0,0,0,0.3);
  color: inherit;
  font-size: 0.95em;
  transition: all 0.2s;
}

#lobby input:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(0,0,0,0.5);
}

button {
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  background: var(--accent);
  color: #001;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9em;
}

button:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

#roomsList {
  max-height: 240px;
  overflow-y: auto;
  margin-top: 12px;
}

.roomItem {
  background: rgba(0,0,0,0.3);
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
}

.roomItem:hover {
  border-color: var(--accent);
  background: rgba(16,185,129,0.1);
}

.roomItem button {
  padding: 6px 12px;
  font-size: 0.85em;
}

#onlineUsers {
  max-height: 300px;
  overflow-y: auto;
}

.online-player {
  background: rgba(0,0,0,0.3);
  padding: 10px;
  margin-bottom: 6px;
  border-radius: 6px;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}

.online-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

#roomLink {
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.3);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

#roomLink.hidden {
  display: none;
}

#roomLink p {
  flex: 1;
  margin: 0;
}

#gameArea {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

#boardContainer {
  background: linear-gradient(180deg, #1f2937, #0b1220);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid var(--border);
  display: inline-block;
}

canvas {
  display: block;
  border-radius: 8px;
  cursor: pointer;
}

#side {
  flex: 1;
  min-width: 280px;
}

#gameInfo {
  background: rgba(255,255,255,0.03);
  padding: 15px;
  border-radius: 12px;
  border: 1px solid var(--border);
  margin-bottom: 15px;
}

#gameInfo p {
  margin: 8px 0;
  font-size: 0.95em;
}

#turnInfo {
  font-weight: 700;
  color: var(--accent);
  font-size: 1.1em !important;
}

#timer {
  color: #fbbf24;
  font-weight: 600;
}

#gameSettings {
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  margin-bottom: 15px;
}

#gameSettings label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 0.9em;
}

#chat {
  background: rgba(255,255,255,0.03);
  padding: 15px;
  border-radius: 12px;
  border: 1px solid var(--border);
}

#chat h4 {
  margin: 0 0 10px 0;
  color: var(--accent);
}

#chatLog {
  height: 200px;
  overflow-y: auto;
  padding: 10px;
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid var(--border);
}

#chatLog::-webkit-scrollbar {
  width: 6px;
}

#chatLog::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
}

#chatLog::-webkit-scrollbar-thumb {
  background: var(--accent);
  border-radius: 4px;
}

.system-message {
  color: var(--muted);
  font-style: italic;
  font-size: 0.85em;
  margin: 6px 0;
  padding: 6px 8px;
  background: rgba(148,163,184,0.1);
  border-radius: 4px;
}

.user-message {
  margin: 8px 0;
  padding: 8px 10px;
  background: rgba(255,255,255,0.05);
  border-radius: 6px;
  font-size: 0.9em;
}

#chatInput {
  width: 100%;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: rgba(0,0,0,0.3);
  color: inherit;
  font-size: 0.9em;
}

#chatInput:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(0,0,0,0.5);
}

.hidden {
  display: none !important;
}

@media (max-width: 900px) {
  #controls {
    flex-direction: column;
  }
  
  #gameArea {
    flex-direction: column;
  }
  
  #boardContainer {
    width: 100%;
  }
  
  canvas {
    width: 100%;
    height: auto;
  }
  
  #side {
    width: 100%;
  }
}'''

print("✅ Created enhanced style.css")
print("📄 Size:", len(style_css), "bytes")
