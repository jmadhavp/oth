// main.js — Enhanced Othello logic + firebase realtime sync with authentication and presence
import { ref, push, set, onValue, remove, update, onDisconnect, get, query, orderByChild, limitToLast } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';
import { db, auth, initAuth, setupPresence } from './firebase.js';

// --- Helpers & DOM 
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

// --- Game state
let localPlayerId = '';
let localName = '';
let currentRoom = null;
let gameRef = null;
let roomRef = ref(db, 'rooms');
let moveTimerEnabled = true;
let timerInterval = null;
let gameTimerValue = 30; // Default timer value in seconds
const SIZE = 8;
let cellSize = Math.floor(boardCanvas.width / SIZE);
let onlineUsers = {};

// Initialize auth and get user ID
(async function initializeApp() {
    try {
        // Load saved name if exists
        const savedName = localStorage.getItem('playerName');
        if (savedName) {
            playerNameInput.value = savedName;
            localName = savedName;
        }
        
        // Initialize authentication
        const user = await initAuth();
        if (user) {
            localPlayerId = user.uid;
            statusEl.textContent = 'Connected';
            
            // Setup presence system
            await setupPresence(localPlayerId);
            
            // Listen for online users
            listenForOnlineUsers();
            
            // Check for room in URL
            const roomFromUrl = getRoomFromUrl();
            if (roomFromUrl) {
                joinRoom(roomFromUrl);
            }
            
            // Refresh lobby
            refreshLobby();
        } else {
            statusEl.textContent = 'Failed to connect';
        }
    } catch (error) {
        console.error("Initialization error:", error);
        statusEl.textContent = 'Connection error';
    }
})();

// --- Helper functions 
function emptyBoard(){ 
  const b = Array.from({length:SIZE},()=>Array.from({length:SIZE},()=>null)); 
  b[3][3]='W'; b[3][4]='B'; b[4][3]='B'; b[4][4]='W'; 
  return b; 
}

function drawBoard(board){ 
  ctx.clearRect(0,0,boardCanvas.width,boardCanvas.height); 
  ctx.fillStyle = '#144729'; 
  ctx.fillRect(0,0,boardCanvas.width,boardCanvas.height); 
  for(let r=0;r<SIZE;r++){ 
    for(let c=0;c<SIZE;c++){ 
      let x=c*cellSize, y=r*cellSize; 
      ctx.strokeStyle='#072b18'; 
      ctx.lineWidth=2; 
      ctx.strokeRect(x+1,y+1,cellSize-2,cellSize-2); 
      const v=board[r][c]; 
      if(v){ 
        ctx.beginPath(); 
        ctx.arc(x+cellSize/2,y+cellSize/2,cellSize*0.38,0,Math.PI*2); 
        ctx.fillStyle=v==='B'?'#000':'#fff'; 
        ctx.shadowColor='#000a';
        ctx.shadowBlur=6; 
        ctx.fill();
        ctx.shadowBlur=0; 
        ctx.closePath(); 
      } 
    } 
  } 
}

function getRoomFromUrl(){ 
  const p=new URLSearchParams(location.search); 
  return p.get('room'); 
}

// --- Online users system
function listenForOnlineUsers() {
  const onlineRef = ref(db, 'online');
  onValue(onlineRef, (snapshot) => {
    const data = snapshot.val() || {};
    onlineUsers = data;
    updateOnlineUsersDisplay();
  });
}

function updateOnlineUsersDisplay() {
  // Create online users element if it doesn't exist
  let onlineUsersEl = $('#onlineUsers');
  if (!onlineUsersEl) {
    onlineUsersEl = document.createElement('div');
    onlineUsersEl.id = 'onlineUsers';
    onlineUsersEl.className = 'online-users';
    $('#side').insertBefore(onlineUsersEl, $('#chat'));
  }
  
  // Count and display online users
  const userCount = Object.keys(onlineUsers).length;
  const userList = Object.values(onlineUsers)
    .map(user => user.displayName)
    .join(', ');
  
  onlineUsersEl.innerHTML = `
    <div class="online-count">👥 Online Players: ${userCount}</div>
    <div class="online-list">${userList}</div>
  `;
}

// --- Firebase lobby actions 
async function refreshLobby() {
  // Use query to get only active rooms
  const activeRoomsQuery = query(roomRef, orderByChild('closed'), limitToLast(10));
  onValue(activeRoomsQuery, snap => {
    const data = snap.val() || {};
    roomsList.innerHTML = '';
    
    // Filter for open rooms
    const open = Object.entries(data)
      .filter(([k, v]) => !v.closed && Object.keys(v.players || {}).length < 2)
      .sort((a, b) => b[1].created - a[1].created); // Sort by newest first
    
    if (open.length === 0) {
      roomsList.innerHTML = '<div class="no-rooms">No open rooms available</div>';
    } else {
      open.forEach(([k, room]) => {
        const playerCount = Object.keys(room.players || {}).length;
        const el = document.createElement('div');
        el.className = 'roomItem';
        
        // Show room creator name if available
        const creator = Object.values(room.players || {})[0]?.name || 'Unknown';
        
        el.innerHTML = `
          <div class="room-info">
            <div class="room-id">Room <b>${k}</b></div>
            <div class="room-players">👤 ${playerCount}/2</div>
            <div class="room-creator">Created by: ${creator}</div>
          </div>
          <button class="join-btn" data-room="${k}">Join</button>
        `;
        el.querySelector('button').onclick = () => joinRoom(k);
        roomsList.appendChild(el);
      });
    }
    
    // Update status with room count
    statusEl.textContent = `Connected - ${open.length} open rooms`;
  });
}

async function createRoom() {
  // Save player name to localStorage
  localName = playerNameInput.value.trim() || ('Guest_' + localPlayerId.slice(-4));
  localStorage.setItem('playerName', localName);
  
  const r = push(roomRef);
  const id = r.key;
  
  // Enhanced room object with metadata
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
    gameState: 'waiting', // waiting, playing, finished
    lastMove: null,
    moveHistory: {},
    settings: {
      timerEnabled: moveTimerEnabled,
      timerValue: gameTimerValue
    }
  };
  
  await set(ref(db, 'rooms/' + id), roomObj);
  
  // Handle disconnection
  onDisconnect(ref(db, 'rooms/' + id + '/players/' + localPlayerId)).remove();
  
  // Auto-close room if creator leaves
  onDisconnect(ref(db, 'rooms/' + id + '/closed')).set(true);
  
  enterRoom(id);
}

async function joinRoom(id) {
  // Save player name
  localName = playerNameInput.value.trim() || ('Guest_' + localPlayerId.slice(-4));
  localStorage.setItem('playerName', localName);
  
  try {
    const roomSnap = await get(ref(db, 'rooms/' + id));
    const room = roomSnap.val();
    
    // Check if room exists
    if (!room) {
      alert('Room not found');
      return;
    }
    
    // Check if room is closed
    if (room.closed) {
      alert('This room is closed');
      return;
    }
    
    const players = room.players || {};
    
    // Check if room is full
    if (Object.keys(players).length >= 2) {
      alert('Room is full');
      return;
    }
    
    // Check if player is already in the room
    if (players[localPlayerId]) {
      enterRoom(id);
      return;
    }
    
    // Assign opposite color to the other player
    const assignedColor = Object.values(players).some(pl => pl.color === 'B') ? 'W' : 'B';
    
    // Join room
    await update(ref(db, 'rooms/' + id + '/players/' + localPlayerId), {
      name: localName,
      color: assignedColor,
      ready: true,
      lastActive: Date.now()
    });
    
    // Handle disconnection
    onDisconnect(ref(db, 'rooms/' + id + '/players/' + localPlayerId)).remove();
    
    // Update game state if both players are present
    if (Object.keys(players).length === 1) {
      await update(ref(db, 'rooms/' + id), {
        gameState: 'playing',
        lastMoveTime: Date.now()
      });
      
      // Add system message
      const chatRef = push(ref(db, 'rooms/' + id + '/chat'));
      await set(chatRef, {
        system: true,
        text: `${localName} joined the game. Game started!`,
        t: Date.now()
      });
    }
    
    enterRoom(id);
  } catch (error) {
    console.error("Error joining room:", error);
    alert('Failed to join room');
  }
}

async function randomJoin() {
  try {
    const snap = await get(roomRef);
    const data = snap.val() || {};
    
    // Find an open room with one player
    const open = Object.entries(data)
      .filter(([k, v]) => !v.closed && Object.keys(v.players || {}).length === 1)
      .sort(() => Math.random() - 0.5); // Randomize order
    
    if (open.length > 0) {
      return joinRoom(open[0][0]);
    }
    
    // No open rooms, create a new one
    return createRoom();
  } catch (error) {
    console.error("Error in random join:", error);
    alert('Failed to join a random game');
  }
}

function enterRoom(id) {
  currentRoom = id;
  roomIdEl.textContent = id;
  roomLinkEl.classList.remove('hidden');
  
  // Update URL with room ID
  history.replaceState(null, '', '?room=' + id);
  
  // Set game reference
  gameRef = ref(db, 'rooms/' + id);
  
  // Bind room listeners
  bindRoomListeners();
  
  // Update player's last active timestamp periodically
  if (heartbeatInterval) clearInterval(heartbeatInterval);
  heartbeatInterval = setInterval(() => {
    if (currentRoom && localPlayerId) {
      update(ref(db, 'rooms/' + currentRoom + '/players/' + localPlayerId), {
        lastActive: Date.now()
      });
    }
  }, 30000); // Update every 30 seconds
}

function leaveRoom() {
  if (!currentRoom) return;
  
  // Clear intervals
  if (heartbeatInterval) clearInterval(heartbeatInterval);
  if (timerInterval) clearInterval(timerInterval);
  
  // Remove player from room
  remove(ref(db, 'rooms/' + currentRoom + '/players/' + localPlayerId));
  
  // Add system message about player leaving
  const chatRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
  set(chatRef, {
    system: true,
    text: `${localName} left the game.`,
    t: Date.now()
  });
  
  // Reset state
  currentRoom = null;
  gameRef = null;
  
  // Update UI
  roomLinkEl.classList.add('hidden');
  history.replaceState(null, '', location.pathname);
  
  // Refresh lobby
  refreshLobby();
}

// --- Room listeners and game state synchronization
let heartbeatInterval = null;

function bindRoomListeners() {
  if (!gameRef) return;
  
  onValue(gameRef, snap => {
    const room = snap.val();
    
    // Handle room closed or deleted
    if (!room) {
      statusEl.textContent = 'Room closed';
      return;
    }
    
    // Draw the game board
    drawBoard(room.board);
    
    // Update turn information with player name
    const currentPlayer = Object.values(room.players || {}).find(p => p.color === room.currentTurn);
    turnInfo.textContent = `Turn: ${currentPlayer ? currentPlayer.name : '?'} (${room.currentTurn})`;
    
    // Update players information with status indicators
    const playersList = Object.values(room.players || {}).map(p => {
      const isCurrentTurn = p.color === room.currentTurn;
      const statusIndicator = isCurrentTurn ? '🎮' : '⏳';
      return `${statusIndicator} ${p.name} (${p.color})`;
    }).join(', ');
    
    playersInfo.textContent = `Players: ${playersList}`;
    
    // Update game state display
    updateGameStateDisplay(room);
    
    // Update chat with system messages
    updateChatDisplay(room.chat);
    
    // Handle game timer if enabled
    handleGameTimer(room);
    
    // Check for game over conditions
    checkGameOver(room);
  });
}

function updateGameStateDisplay(room) {
  // Create or update game state element
  let gameStateEl = $('#gameState');
  if (!gameStateEl) {
    gameStateEl = document.createElement('div');
    gameStateEl.id = 'gameState';
    $('#side').insertBefore(gameStateEl, $('#players'));
  }
  
  // Display game state
  let stateText = '';
  switch (room.gameState) {
    case 'waiting':
      stateText = 'Waiting for opponent...';
      break;
    case 'playing':
      stateText = 'Game in progress';
      break;
    case 'finished':
      stateText = room.winner ? `Game over - ${room.winner} wins!` : 'Game over - Draw!';
      break;
    default:
      stateText = 'Unknown state';
  }
  
  gameStateEl.textContent = stateText;
  
  // Show valid moves for current player
  if (room.gameState === 'playing' && room.currentTurn === getMyColor(room)) {
    highlightValidMoves(room.board, room.currentTurn);
  }
}

function updateChatDisplay(chat) {
  chatLog.innerHTML = '';
  
  if (!chat) return;
  
  // Convert to array and sort by timestamp
  const messages = Object.values(chat).sort((a, b) => a.t - b.t);
  
  messages.forEach(m => {
    const d = document.createElement('div');
    
    if (m.system) {
      // System message
      d.className = 'system-message';
      d.textContent = m.text;
    } else {
      // User message
      d.className = 'user-message';
      d.textContent = `${m.from}: ${m.text}`;
    }
    
    chatLog.appendChild(d);
  });
  
  // Scroll to bottom
  chatLog.scrollTop = chatLog.scrollHeight;
}

function getMyColor(room) {
  return room.players?.[localPlayerId]?.color || null;
}

function highlightValidMoves(board, color) {
  const moves = validMoves(board, color);
  
  // Clear previous highlights
  ctx.globalAlpha = 1;
  
  // Draw valid move indicators
  ctx.globalAlpha = 0.4;
  moves.forEach(([r, c]) => {
    const x = c * cellSize + cellSize / 2;
    const y = r * cellSize + cellSize / 2;
    
    ctx.beginPath();
    ctx.arc(x, y, cellSize * 0.2, 0, Math.PI * 2);
    ctx.fillStyle = color === 'B' ? '#000' : '#fff';
    ctx.fill();
    ctx.closePath();
  });
  
  ctx.globalAlpha = 1;
}

function checkGameOver(room) {
  // Skip if game is not in playing state
  if (room.gameState !== 'playing') return;
  
  const board = room.board;
  
  // Check if both players have valid moves
  const blackMoves = validMoves(board, 'B');
  const whiteMoves = validMoves(board, 'W');
  
  // If neither player has valid moves, game is over
  if (blackMoves.length === 0 && whiteMoves.length === 0) {
    endGame(room);
  }
  
  // If current player has no moves, switch turns
  if ((room.currentTurn === 'B' && blackMoves.length === 0) ||
      (room.currentTurn === 'W' && whiteMoves.length === 0)) {
    
    // Add system message about skipping turn
    const chatRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
    set(chatRef, {
      system: true,
      text: `${room.currentTurn === 'B' ? 'Black' : 'White'} has no valid moves. Turn skipped.`,
      t: Date.now()
    });
    
    // Switch turns
    const nextTurn = room.currentTurn === 'B' ? 'W' : 'B';
    update(ref(db, 'rooms/' + currentRoom), {
      currentTurn: nextTurn,
      lastMoveTime: Date.now()
    });
  }
}

async function endGame(room) {
  // Count pieces to determine winner
  const board = room.board;
  let blackCount = 0;
  let whiteCount = 0;
  
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (board[r][c] === 'B') blackCount++;
      else if (board[r][c] === 'W') whiteCount++;
    }
  }
  
  // Determine winner
  let winner = null;
  if (blackCount > whiteCount) winner = 'B';
  else if (whiteCount > blackCount) winner = 'W';
  
  // Update game state
  await update(ref(db, 'rooms/' + currentRoom), {
    gameState: 'finished',
    winner: winner,
    finalScore: {
      B: blackCount,
      W: whiteCount
    }
  });
  
  // Add system message
  const chatRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
  let winnerText = winner ? 
    `Game over! ${winner === 'B' ? 'Black' : 'White'} wins (${blackCount}-${whiteCount})` : 
    `Game over! It's a draw (${blackCount}-${whiteCount})`;
  
  await set(chatRef, {
    system: true,
    text: winnerText,
    t: Date.now()
  });
}

// --- Game Timer
let timerInterval = null;

function handleGameTimer(room) {
  // Clear existing timer
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  
  // Check if timer is enabled in room settings
  const timerEnabled = room.settings?.timerEnabled ?? moveTimerEnabled;
  if (!timerEnabled || room.gameState !== 'playing') {
    timerEl.textContent = 'Timer: disabled';
    return;
  }
  
  // Get timer value from settings or use default
  const timerValue = room.settings?.timerValue ?? gameTimerValue;
  
  // Calculate remaining time
  const lastMoveTime = room.lastMoveTime || Date.now();
  const elapsedSeconds = Math.floor((Date.now() - lastMoveTime) / 1000);
  let remainingSeconds = Math.max(0, timerValue - elapsedSeconds);
  
  // Update timer display
  updateTimerDisplay(remainingSeconds);
  
  // Start timer interval
  timerInterval = setInterval(() => {
    remainingSeconds--;
    
    // Update display
    updateTimerDisplay(remainingSeconds);
    
    // Handle timer expiration
    if (remainingSeconds <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
      
      // Only handle expiration if it's the current player's turn
      if (room.currentTurn === getMyColor(room)) {
        handleTimerExpiration(room);
      }
    }
  }, 1000);
}

function updateTimerDisplay(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  // Format time as MM:SS
  const formattedTime = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  
  // Update display with color coding
  if (seconds <= 10) {
    timerEl.innerHTML = `Timer: <span style="color: red; font-weight: bold;">${formattedTime}</span>`;
  } else {
    timerEl.textContent = `Timer: ${formattedTime}`;
  }
}

async function handleTimerExpiration(room) {
  // Add system message
  const chatRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
  await set(chatRef, {
    system: true,
    text: `Time's up for ${room.currentTurn === 'B' ? 'Black' : 'White'}! Turn skipped.`,
    t: Date.now()
  });
  
  // Switch turns
  const nextTurn = room.currentTurn === 'B' ? 'W' : 'B';
  await update(ref(db, 'rooms/' + currentRoom), {
    currentTurn: nextTurn,
    lastMoveTime: Date.now()
  });
}

// --- Enhanced Chat System
chatInput.addEventListener('keypress', async e => {
  if (e.key === 'Enter' && currentRoom) {
    const text = chatInput.value.trim();
    if (!text) return;
    
    // Clear input
    chatInput.value = '';
    
    // Get player name
    const playerName = playerNameInput.value.trim() || localName || 'Guest_' + localPlayerId.slice(-4);
    
    // Create chat message
    const cRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
    await set(cRef, {
      from: playerName,
      text: text,
      playerId: localPlayerId,
      color: getMyColor(room) || 'guest',
      t: Date.now()
    });
    
    // Scroll chat to bottom
    setTimeout(() => {
      chatLog.scrollTop = chatLog.scrollHeight;
    }, 100);
  }
});

// --- Othello rules: directions and flipping 
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
  let flippedPieces = [];
  
  for (const [dr, dc] of dirs) { 
    let line = [];
    let rr = r + dr, cc = c + dc; 
    
    while (rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === opponent) {
      line.push([rr, cc]);
      rr += dr;
      cc += dc;
    } 
    
    if (line.length > 0 && rr >= 0 && rr < SIZE && cc >= 0 && cc < SIZE && board[rr][cc] === color) { 
      for (const [pR, pC] of line) {
        board[pR][pC] = color;
        flippedPieces.push([pR, pC]);
      } 
      flipped = true; 
    } 
  } 
  
  if (flipped) {
    board[r][c] = color;
    flippedPieces.push([r, c]);
  } 
  
  return { flipped, flippedPieces };
}

// Enhanced board click handler with animation and improved validation
boardCanvas.addEventListener('click', async ev => {
  // Check if in a room and game is active
  if (!currentRoom) return;
  
  try {
    // Get room data
    const snap = await get(gameRef);
    const room = snap.val();
    
    // Validate game state
    if (!room || room.gameState !== 'playing') return;
    
    // Get player color and validate turn
    const myColor = getMyColor(room);
    if (!myColor || room.currentTurn !== myColor) return;
    
    // Calculate board coordinates from click
    const rect = boardCanvas.getBoundingClientRect();
    const x = Math.floor((ev.clientX - rect.left) / cellSize);
    const y = Math.floor((ev.clientY - rect.top) / cellSize);
    
    // Validate coordinates
    if (x < 0 || x >= SIZE || y < 0 || y >= SIZE) return;
    
    // Check if cell is empty
    const board = JSON.parse(JSON.stringify(room.board)); // Deep copy
    if (board[y][x]) return;
    
    // Check if move is valid
    const moves = validMoves(board, myColor);
    if (!moves.some(([r, c]) => r === y && c === x)) return;
    
    // Apply move and get flipped pieces
    const { flipped, flippedPieces } = applyMove(board, y, x, myColor);
    if (!flipped) return;
    
    // Switch turns
    const next = myColor === 'B' ? 'W' : 'B';
    
    // Record move in history
    const moveHistory = room.moveHistory || {};
    const moveCount = Object.keys(moveHistory).length;
    moveHistory[moveCount] = {
      player: localPlayerId,
      color: myColor,
      position: [y, x],
      flipped: flippedPieces.length - 1, // Subtract the placed piece
      timestamp: Date.now()
    };
    
    // Update game state in Firebase
    await update(gameRef, {
      board,
      currentTurn: next,
      lastMove: [y, x],
      lastMoveTime: Date.now(),
      moveHistory
    });
    
    // Play sound effect
    document.getElementById('sndPlace').play().catch(() => {});
    
    // Add move to chat as system message
    const chatRef = push(ref(db, 'rooms/' + currentRoom + '/chat'));
    await set(chatRef, {
      system: true,
      text: `${localName} (${myColor}) placed at [${x+1},${y+1}] and flipped ${flippedPieces.length - 1} pieces.`,
      t: Date.now()
    });
  } catch (error) {
    console.error("Error making move:", error);
  }
});

// --- UI binding createRoomBtn.onclick=createRoom; refreshRoomsBtn.onclick=refreshLobby; randomJoinBtn.onclick=randomJoin; leaveRoomBtn.onclick=leaveRoom; copyLinkBtn.onclick=()=>{navigator.clipboard.writeText(location.href);alert('Link copied');}; $('#moveTimerToggle').addEventListener('change',e=>moveTimerEnabled=e.target.checked); window.addEventListener('load',()=>{const r=getRoomFromUrl();refreshLobby();if(r)joinRoom(r);});