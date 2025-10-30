// main.js — FIXED to update presence when name changes

import { ref, push, set, onValue, remove, update, onDisconnect, get, query, orderByChild, limitToLast } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';
import { db, auth, initAuth, setupPresence, updatePresenceName, listenToOnlineUsers } from './firebase.js';

// DOM Elements
const $ = sel => document.querySelector(sel);
const playerNameInput = $('#playerName');
const createRoomBtn = $('#createRoom');
const refreshRoomsBtn = $('#refreshRooms');
const roomsList = $('#roomsList');
const roomLinkEl = $('#roomLink');
const roomIdEl = $('#roomId');
const copyLinkBtn = $('#copyLink');
const leaveRoomBtn = $('#leaveRoom');
const randomJoinBtn = $('#randomJoin');
const chatLog = $('#chatLog');
const chatInput = $('#chatInput');
const boardCanvas = $('#board');
const ctx = boardCanvas.getContext('2d');
const turnInfo = $('#turnInfo');
const playersInfo = $('#players');
const timerEl = $('#timer');
const statusEl = $('#status');
const onlineCountEl = $('#onlineCount');
const onlineUsersEl = $('#onlineUsers');

// Game State
let localPlayerId = '';
let localName = '';
let currentRoom = null;
let gameRef = null;
const roomRef = ref(db, 'rooms');
let moveTimerEnabled = true;
let timerInterval = null;
const gameTimerValue = 30;
const SIZE = 8;
const cellSize = Math.floor(boardCanvas.width / SIZE);
let onlineUsers = {};
let isPresenceSetup = false;

// Initialize Application
(async function initializeApp() {
  try {
    statusEl.textContent = '🔄 Connecting...';
    
    // Load saved name
    const savedName = localStorage.getItem('playerName');
    if (savedName) {
      playerNameInput.value = savedName;
      localName = savedName;
    }

    // Initialize auth first
    const user = await initAuth();
    if (user) {
      localPlayerId = user.uid;
      statusEl.textContent = '✅ Connected';
      
      // DON'T setup presence yet - wait for name input
      console.log('🎮 Ready to play! Enter your name and create/join a room');
      
      // Listen for online users
      listenToOnlineUsers((users) => {
        onlineUsers = users;
        updateOnlineUsersDisplay();
      });
      
      // Check for room in URL
      const roomFromUrl = getRoomFromUrl();
      if (roomFromUrl) {
        await joinRoom(roomFromUrl);
      }
      
      // Refresh lobby
      refreshLobby();
    } else {
      statusEl.textContent = '❌ Connection failed';
    }
  } catch (error) {
    console.error('Init error:', error);
    statusEl.textContent = '❌ Error: ' + error.message;
  }
})();

// Update presence when name changes
playerNameInput.addEventListener('blur', async () => {
  const newName = playerNameInput.value.trim();
  if (newName && newName !== localName) {
    localName = newName;
    localStorage.setItem('playerName', localName);
    
    // Update presence with new name
    if (isPresenceSetup) {
      await updatePresenceName(localPlayerId, localName);
      console.log('📝 Name updated to:', localName);
    } else {
      // First time setup
      await setupPresence(localPlayerId, localName);
      isPresenceSetup = true;
      console.log('✅ Presence setup with name:', localName);
    }
  }
});

// Also update on Enter key
playerNameInput.addEventListener('keypress', async (e) => {
  if (e.key === 'Enter') {
    playerNameInput.blur(); // Trigger the blur event
  }
});

// Helper Functions
function getRoomFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get('room');
}

function emptyBoard() {
  const b = Array.from({length:SIZE}, () => Array.from({length:SIZE}, () => null));
  b[3][3] = 'W'; b[3][4] = 'B';
  b[4][3] = 'B'; b[4][4] = 'W';
  return b;
}

function drawBoard(board) {
  ctx.clearRect(0, 0, boardCanvas.width, boardCanvas.height);
  
  // Draw green felt background
  ctx.fillStyle = '#144729';
  ctx.fillRect(0, 0, boardCanvas.width, boardCanvas.height);
  
  // Draw grid lines
  ctx.strokeStyle = '#0a2817';
  ctx.lineWidth = 2;
  for (let i = 0; i <= SIZE; i++) {
    ctx.beginPath();
    ctx.moveTo(i * cellSize, 0);
    ctx.lineTo(i * cellSize, boardCanvas.height);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(0, i * cellSize);
    ctx.lineTo(boardCanvas.width, i * cellSize);
    ctx.stroke();
  }
  
  // Draw pieces
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (board[r][c]) {
        drawPiece(r, c, board[r][c]);
      }
    }
  }
}

function drawPiece(r, c, color) {
  const x = c * cellSize + cellSize / 2;
  const y = r * cellSize + cellSize / 2;
  const radius = cellSize * 0.4;
  
  // Draw piece shadow
  ctx.beginPath();
  ctx.arc(x + 2, y + 2, radius, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.fill();
  
  // Draw piece
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  
  if (color === 'B') {
    const grad = ctx.createRadialGradient(x - radius/3, y - radius/3, 0, x, y, radius);
    grad.addColorStop(0, '#555');
    grad.addColorStop(1, '#000');
    ctx.fillStyle = grad;
  } else {
    const grad = ctx.createRadialGradient(x - radius/3, y - radius/3, 0, x, y, radius);
    grad.addColorStop(0, '#fff');
    grad.addColorStop(1, '#ddd');
    ctx.fillStyle = grad;
  }
  
  ctx.fill();
  ctx.strokeStyle = color === 'B' ? '#000' : '#ccc';
  ctx.lineWidth = 2;
  ctx.stroke();
}

function updateOnlineUsersDisplay() {
  const userCount = Object.keys(onlineUsers).length;
  onlineCountEl.textContent = `👥 Online: ${userCount}`;
  
  if (userCount === 0) {
    onlineUsersEl.innerHTML = '<p style="color:#94a3b8;font-size:0.9em;padding:10px">No players online yet</p>';
    return;
  }
  
  const userElements = Object.entries(onlineUsers)
    .sort((a, b) => (b[1].connectedAt || 0) - (a[1].connectedAt || 0))
    .map(([uid, user]) => {
      const isMe = uid === localPlayerId;
      return `
        <div class="online-player">
          <div class="online-indicator"></div>
          <span style="flex:1;font-weight:${isMe ? 'bold' : 'normal'}">
            ${user.displayName || 'Anonymous'}${isMe ? ' (You)' : ''}
          </span>
        </div>
      `;
    }).join('');
  
  onlineUsersEl.innerHTML = userElements;
}

// Room Functions
async function refreshLobby() {
  const activeRoomsQuery = query(roomRef, orderByChild('created'), limitToLast(20));
  
  onValue(activeRoomsQuery, snap => {
    const data = snap.val() || {};
    roomsList.innerHTML = '';
    
    const openRooms = Object.entries(data)
      .filter(([k, v]) => !v.closed && Object.keys(v.players || {}).length < 2)
      .sort((a, b) => b[1].created - a[1].created);
    
    if (openRooms.length === 0) {
      roomsList.innerHTML = '<p style="color:#94a3b8;padding:10px;text-align:center">No open rooms</p>';
    } else {
      openRooms.forEach(([roomId, room]) => {
        const playerCount = Object.keys(room.players || {}).length;
        const creator = Object.values(room.players || {})[0]?.name || 'Unknown';
        
        const el = document.createElement('div');
        el.className = 'roomItem';
        el.innerHTML = `
          <div style="flex:1">
            <strong>Room ${roomId.slice(-6)}</strong>
            <div style="font-size:0.85em;color:#94a3b8">
              👤 ${playerCount}/2 • by ${creator}
            </div>
          </div>
          <button onclick="window.joinRoomById('${roomId}')">Join</button>
        `;
        roomsList.appendChild(el);
      });
    }
  });
}

async function createRoom() {
  localName = playerNameInput.value.trim() || `Guest_${localPlayerId.slice(-4)}`;
  localStorage.setItem('playerName', localName);
  
  // Setup presence with name
  if (!isPresenceSetup) {
    await setupPresence(localPlayerId, localName);
    isPresenceSetup = true;
  } else {
    await updatePresenceName(localPlayerId, localName);
  }
  
  const r = push(roomRef);
  const id = r.key;
  
  const roomObj = {
    created: Date.now(),
    board: emptyBoard(),
    currentTurn: 'B',
    players: {
      [localPlayerId]: {
        name: localName,
        color: 'B',
        ready: true,
        lastActive: Date.now()
      }
    },
    chat: {},
    closed: false,
    gameState: 'waiting',
    lastMoveTime: Date.now(),
    moveHistory: {},
    settings: {
      timerEnabled: moveTimerEnabled,
      timerValue: gameTimerValue
    }
  };
  
  await set(ref(db, `rooms/${id}`), roomObj);
  
  onDisconnect(ref(db, `rooms/${id}/players/${localPlayerId}`)).remove();
  onDisconnect(ref(db, `rooms/${id}/closed`)).set(true);
  
  enterRoom(id);
}

async function joinRoom(id) {
  localName = playerNameInput.value.trim() || `Guest_${localPlayerId.slice(-4)}`;
  localStorage.setItem('playerName', localName);
  
  // Setup presence with name
  if (!isPresenceSetup) {
    await setupPresence(localPlayerId, localName);
    isPresenceSetup = true;
  } else {
    await updatePresenceName(localPlayerId, localName);
  }
  
  try {
    const roomSnap = await get(ref(db, `rooms/${id}`));
    const room = roomSnap.val();
    
    if (!room) {
      alert('Room not found');
      return;
    }
    
    if (room.closed) {
      alert('Room is closed');
      return;
    }
    
    const players = room.players || {};
    
    if (Object.keys(players).length >= 2 && !players[localPlayerId]) {
      alert('Room is full');
      return;
    }
    
    if (players[localPlayerId]) {
      enterRoom(id);
      return;
    }
    
    const assignedColor = Object.values(players).some(pl => pl.color === 'B') ? 'W' : 'B';
    
    await update(ref(db, `rooms/${id}/players/${localPlayerId}`), {
      name: localName,
      color: assignedColor,
      ready: true,
      lastActive: Date.now()
    });
    
    onDisconnect(ref(db, `rooms/${id}/players/${localPlayerId}`)).remove();
    
    if (Object.keys(players).length === 1) {
      await update(ref(db, `rooms/${id}`), {
        gameState: 'playing',
        lastMoveTime: Date.now()
      });
      
      const chatRef = push(ref(db, `rooms/${id}/chat`));
      await set(chatRef, {
        system: true,
        text: `${localName} joined. Game started!`,
        t: Date.now()
      });
    }
    
    enterRoom(id);
  } catch (error) {
    console.error('Join error:', error);
    alert('Failed to join room: ' + error.message);
  }
}

async function randomJoin() {
  try {
    const snap = await get(roomRef);
    const data = snap.val() || {};
    
    const openRooms = Object.entries(data)
      .filter(([k, v]) => !v.closed && Object.keys(v.players || {}).length === 1)
      .sort(() => Math.random() - 0.5);
    
    if (openRooms.length > 0) {
      return joinRoom(openRooms[0][0]);
    }
    
    return createRoom();
  } catch (error) {
    console.error('Random join error:', error);
    alert('Failed to join game');
  }
}

function enterRoom(id) {
  currentRoom = id;
  roomIdEl.textContent = id.slice(-8);
  roomLinkEl.classList.remove('hidden');
  history.replaceState(null, '', '?room=' + id);
  
  gameRef = ref(db, `rooms/${id}`);
  bindRoomListeners();
}

async function leaveRoom() {
  if (!currentRoom) return;
  
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  
  await remove(ref(db, `rooms/${currentRoom}/players/${localPlayerId}`));
  
  const chatRef = push(ref(db, `rooms/${currentRoom}/chat`));
  await set(chatRef, {
    system: true,
    text: `${localName} left the game`,
    t: Date.now()
  });
  
  currentRoom = null;
  gameRef = null;
  roomLinkEl.classList.add('hidden');
  history.replaceState(null, '', location.pathname);
  refreshLobby();
}

// [Rest of the game logic remains the same - board click, chat, timer, etc.]
// Copy all the remaining functions from the previous main.js

// UI Bindings
createRoomBtn.onclick = createRoom;
refreshRoomsBtn.onclick = refreshLobby;
randomJoinBtn.onclick = randomJoin;
leaveRoomBtn.onclick = leaveRoom;
copyLinkBtn.onclick = () => {
  navigator.clipboard.writeText(location.href);
  alert('Link copied!');
};

$('#moveTimerToggle').addEventListener('change', e => {
  moveTimerEnabled = e.target.checked;
});

window.joinRoomById = joinRoom;

console.log('🎮 Othello initialized - Enter your name to appear online!');