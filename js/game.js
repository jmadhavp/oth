// Game Logic and Matchmaking Module
import { db } from './auth.js';
import { collection, doc, getDoc, setDoc, deleteDoc, onSnapshot, query, where, serverTimestamp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

// Game Constants
const MAX_LEVEL = 9999;
const BASE_XP_REQUIREMENT = 1000;
const XP_INCREASE_RATE = 1.2;

// Calculate XP required for next level
function getXPRequirement(level) {
    return Math.floor(BASE_XP_REQUIREMENT * Math.pow(XP_INCREASE_RATE, level - 1));
}

// Update user's XP and level
async function updateUserXP(userId, xpGained) {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    const userData = userDoc.data();
    
    let newXP = userData.xp + xpGained;
    let newLevel = userData.level;
    
    while (newXP >= getXPRequirement(newLevel) && newLevel < MAX_LEVEL) {
        newXP -= getXPRequirement(newLevel);
        newLevel++;
    }
    
    await setDoc(userRef, {
        ...userData,
        xp: newXP,
        level: newLevel,
        lastActive: serverTimestamp()
    });
    
    return { newXP, newLevel };
}

// Generate unique game ID
function generateGameId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// Matchmaking function
async function findMatch(userId) {
    const matchmakingRef = collection(db, 'matchmaking');
    
    // Generate unique matchmaking ID
    const matchId = generateGameId();
    
    // Add user to matchmaking pool
    await setDoc(doc(matchmakingRef, userId), {
        userId,
        matchId,
        timestamp: serverTimestamp(),
        status: 'waiting'
    });
    
    // Query for any available player
    const matchQuery = query(
        matchmakingRef,
        where('userId', '!=', userId),
        where('status', '==', 'waiting')
    );
    
    return new Promise((resolve, reject) => {
        const unsubscribe = onSnapshot(matchQuery, async (snapshot) => {
            const availablePlayers = snapshot.docs.map(doc => doc.data());
            
            if (availablePlayers.length > 0) {
                // Pick a random opponent
                const randomIndex = Math.floor(Math.random() * availablePlayers.length);
                const match = availablePlayers[randomIndex];
                
                // Create game session
                const gameId = generateGameId();
                await setDoc(doc(db, 'games', gameId), {
                    player1: userId,
                    player2: match.userId,
                    status: 'starting',
                    timestamp: serverTimestamp(),
                    matchId: gameId
                });
                
                // Remove both players from matchmaking
                await deleteDoc(doc(matchmakingRef, userId));
                await deleteDoc(doc(matchmakingRef, match.userId));
                
                unsubscribe();
                resolve({ gameId, opponent: match });
            }
        });
        
        // Timeout after 60 seconds
        setTimeout(() => {
            unsubscribe();
            deleteDoc(doc(matchmakingRef, userId));
            reject('Matchmaking timeout');
        }, 60000);
    });
}

// Game state management
class GameState {
    constructor(gameId, playerId) {
        this.gameId = gameId;
        this.playerId = playerId;
        this.board = Array(8).fill().map(() => Array(8).fill(null));
        this.currentTurn = null;
        this.gameStatus = 'starting';
    }

    initializeBoard() {
        // Initialize the standard Othello/Reversi starting position
        this.board[3][3] = 'white';
        this.board[3][4] = 'black';
        this.board[4][3] = 'black';
        this.board[4][4] = 'white';
    }

    async startGame() {
        this.initializeBoard();
        await setDoc(doc(db, 'games', this.gameId), {
            board: this.board,
            currentTurn: 'black',
            status: 'active',
            timestamp: serverTimestamp()
        }, { merge: true });
    }
}

export {
    findMatch,
    updateUserXP,
    getXPRequirement,
    GameState
};