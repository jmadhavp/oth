// main.js — Complete Othello logic with Firebase realtime sync and heartbeat integration

import { ref, push, set, onValue, remove, update, onDisconnect, get, query, orderByChild, limitToLast } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';
import { db, auth, initAuth, setupPresence, listenToOnlineUsers } from './firebase.js';

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

// Initialize Application
(async function initializeApp() {
  try {
    statusEl.textContent = 'Connecting...';
    
    // Load saved name
    const savedName = localStorage.getItem('playerName');
    if (savedName) {
      playerNameInput.value = savedName;
      localName = savedName;
    }

    // Initialize auth
    const user = await initAuth();
    if (user) {
      localPlayerId = user.uid;
      statusEl.textContent = '✅ Connected';
      
      // Get display name
      const displayName = localName || `Guest_${localPlayerId.slice(-4)}`;
      
      // Setup presence with heartbeat
      await setupPresence(localPlayerId, displayName);
      
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
    // Vertical lines
    ctx.beginPath();
    ctx.moveTo(i * cellSize, 0);
    ctx.lineTo(i * cellSize, boardCanvas.height);
    ctx.stroke();
    
    // Horizontal lines
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
    onlineUsersEl.innerHTML = '<p style="color:#94a3b8;font-size:0.9em">No players online</p>';
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
            ${user.displayName}${isMe ? ' (You)' : ''}
          </span>
        </div>
      `;
    }).join('');
  
  onlineUsersEl.innerHTML = userElements;
}

// Lobby Functions
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

// Room Management
async function createRoom() {
  localName = playerNameInput.value.trim() || `Guest_${localPlayerId.slice(-4)}`;
  localStorage.setItem('playerName', localName);
  
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
    alert('Failed to join room');
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

// Game Logic
function bindRoomListeners() {
  if (!gameRef) return;
  
  onValue(gameRef, snap => {
    const room = snap.val();
    
    if (!room) {
      statusEl.textContent = 'Room closed';
      return;
    }
    
    drawBoard(room.board);
    
    const currentPlayer = Object.values(room.players || {})
      .find(p => p.color === room.currentTurn);
    turnInfo.textContent = `Turn: ${currentPlayer ? currentPlayer.name : '?'} (${room.currentTurn})`;
    
    const playersList = Object.values(room.players || {})
      .map(p => {
        const indicator = p.color === room.currentTurn ? '🎮' : '⏳';
        return `${indicator} ${p.name} (${p.color})`;
      }).join(' vs ');
    playersInfo.textContent = playersList;
    
    updateChatDisplay(room.chat);
    handleGameTimer(room);
    checkGameOver(room);
    
    if (room.gameState === 'playing' && room.currentTurn === getMyColor(room)) {
      highlightValidMoves(room.board, room.currentTurn);
    }
  });
}

function getMyColor(room) {
  return room.players?.[localPlayerId]?.color || null;
}

function highlightValidMoves(board, color) {
  const moves = validMoves(board, color);
  
  ctx.globalAlpha = 0.5;
  moves.forEach(([r, c]) => {
    const x = c * cellSize + cellSize / 2;
    const y = r * cellSize + cellSize / 2;
    
    ctx.beginPath();
    ctx.arc(x, y, cellSize * 0.25, 0, Math.PI * 2);
    ctx.fillStyle = color === 'B' ? '#FFD700' : '#FFD700';
    ctx.fill();
  });
  ctx.globalAlpha = 1;
}

function updateChatDisplay(chat) {
  if (!chat) return;
  
  chatLog.innerHTML = '';
  const messages = Object.values(chat).sort((a, b) => a.t - b.t);
  
  messages.forEach(m => {
    const el = document.createElement('div');
    el.className = m.system ? 'system-message' : 'user-message';
    el.textContent = m.system ? m.text : `${m.from}: ${m.text}`;
    chatLog.appendChild(el);
  });
  
  chatLog.scrollTop = chatLog.scrollHeight;
}

function handleGameTimer(room) {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  
  const timerEnabled = room.settings?.timerEnabled ?? moveTimerEnabled;
  if (!timerEnabled || room.gameState !== 'playing') {
    timerEl.textContent = 'Timer: disabled';
    return;
  }
  
  const timerValue = room.settings?.timerValue ?? gameTimerValue;
  const lastMoveTime = room.lastMoveTime || Date.now();
  const elapsedSeconds = Math.floor((Date.now() - lastMoveTime) / 1000);
  let remainingSeconds = Math.max(0, timerValue - elapsedSeconds);
  
  updateTimerDisplay(remainingSeconds);
  
  timerInterval = setInterval(() => {
    remainingSeconds--;
    updateTimerDisplay(remainingSeconds);
    
    if (remainingSeconds <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
      
      if (room.currentTurn === getMyColor(room)) {
        handleTimerExpiration(room);
      }
    }
  }, 1000);
}

function updateTimerDisplay(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  const formatted = `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  
  timerEl.innerHTML = seconds <= 10 ? 
    `<span style="color:#ef4444">⏰ ${formatted}</span>` :
    `Timer: ${formatted}`;
}

async function handleTimerExpiration(room) {
  const chatRef = push(ref(db, `rooms/${currentRoom}/chat`));
  await set(chatRef, {
    system: true,
    text: `Time's up for ${room.currentTurn}! Turn skipped.`,
    t: Date.now()
  });
  
  const nextTurn = room.currentTurn === 'B' ? 'W' : 'B';
  await update(ref(db, `rooms/${currentRoom}`), {
    currentTurn: nextTurn,
    lastMoveTime: Date.now()
  });
}

function checkGameOver(room) {
  if (room.gameState !== 'playing') return;
  
  const board = room.board;
  const blackMoves = validMoves(board, 'B');
  const whiteMoves = validMoves(board, 'W');
  
  if (blackMoves.length === 0 && whiteMoves.length === 0) {
    endGame(room);
    return;
  }
  
  if ((room.currentTurn === 'B' && blackMoves.length === 0) ||
      (room.currentTurn === 'W' && whiteMoves.length === 0)) {
    const chatRef = push(ref(db, `rooms/${currentRoom}/chat`));
    set(chatRef, {
      system: true,
      text: `${room.currentTurn} has no valid moves. Turn skipped.`,
      t: Date.now()
    });
    
    const nextTurn = room.currentTurn === 'B' ? 'W' : 'B';
    update(ref(db, `rooms/${currentRoom}`), {
      currentTurn: nextTurn,
      lastMoveTime: Date.now()
    });
  }
}

async function endGame(room) {
  const board = room.board;
  let blackCount = 0, whiteCount = 0;
  
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (board[r][c] === 'B') blackCount++;
      else if (board[r][c] === 'W') whiteCount++;
    }
  }
  
  let winner = null;
  if (blackCount > whiteCount) winner = 'B';
  else if (whiteCount > blackCount) winner = 'W';
  
  await update(ref(db, `rooms/${currentRoom}`), {
    gameState: 'finished',
    winner: winner,
    finalScore: { B: blackCount, W: whiteCount }
  });
  
  const chatRef = push(ref(db, `rooms/${currentRoom}/chat`));
  const winnerText = winner ?
    `Game over! ${winner === 'B' ? 'Black' : 'White'} wins (${blackCount}-${whiteCount})` :
    `Game over! Draw (${blackCount}-${whiteCount})`;
  
  await set(chatRef, {
    system: true,
    text: winnerText,
    t: Date.now()
  });
}

// Othello Rules
const dirs = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]];

function validMoves(board, color) {
  const opponent = color === 'B' ? 'W' : 'B';
  const moves = [];
  
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (board[r][c]) continue;
      
      for (const [dr, dc] of dirs) {
        let rr = r + dr, cc = c + dc, foundOpp = false;
        
        while (rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === opponent) {
          foundOpp = true;
          rr += dr;
          cc += dc;
        }
        
        if (foundOpp && rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === color) {
          moves.push([r, c]);
          break;
        }
      }
    }
  }
  
  return moves;
}

function applyMove(board, r, c, color) {
  const opponent = color === 'B' ? 'W' : 'B';
  let flipped = false;
  
  for (const [dr, dc] of dirs) {
    const line = [];
    let rr = r + dr, cc = c + dc;
    
    while (rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === opponent) {
      line.push([rr, cc]);
      rr += dr;
      cc += dc;
    }
    
    if (line.length > 0 && rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === color) {
      for (const [pR, pC] of line) {
        board[pR][pC] = color;
      }
      flipped = true;
    }
  }
  
  if (flipped) {
    board[r][c] = color;
  }
  
  return flipped;
}

// Board Click Handler
boardCanvas.addEventListener('click', async ev => {
  if (!currentRoom) return;
  
  try {
    const snap = await get(gameRef);
    const room = snap.val();
    
    if (!room || room.gameState !== 'playing') return;
    
    const myColor = getMyColor(room);
    if (!myColor || room.currentTurn !== myColor) return;
    
    const rect = boardCanvas.getBoundingClientRect();
    const x = Math.floor((ev.clientX - rect.left) / cellSize);
    const y = Math.floor((ev.clientY - rect.top) / cellSize);
    
    if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return;
    
    const board = JSON.parse(JSON.stringify(room.board));
    if (board[y][x]) return;
    
    const moves = validMoves(board, myColor);
    if (!moves.some(([r, c]) => r === y && c === x)) return;
    
    if (!applyMove(board, y, x, myColor)) return;
    
    const next = myColor === 'B' ? 'W' : 'B';
    
    await update(gameRef, {
      board,
      currentTurn: next,
      lastMove: [y, x],
      lastMoveTime: Date.now()
    });
    
    $('#sndPlace').play().catch(() => {});
    
    const chatRef = push(ref(db, `rooms/${currentRoom}/chat`));
    await set(chatRef, {
      system: true,
      text: `${localName} (${myColor}) placed at [${x+1},${y+1}]`,
      t: Date.now()
    });
  } catch (error) {
    console.error('Move error:', error);
  }
});

// Chat Handler
chatInput.addEventListener('keypress', async e => {
  if (e.key === 'Enter' && currentRoom) {
    const text = chatInput.value.trim();
    if (!text) return;
    
    chatInput.value = '';
    
    const cRef = push(ref(db, `rooms/${currentRoom}/chat`));
    await set(cRef, {
      from: localName,
      text: text,
      t: Date.now()
    });
  }
});

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

// Global join function for HTML onclick
window.joinRoomById = joinRoom;

console.log('🎮 Othello game initialized with heartbeat presence');