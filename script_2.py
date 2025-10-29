
# 3. Create PERFECT firebase.js with HEARTBEAT mechanism
firebase_js = '''// firebase.js - Enhanced with ROBUST heartbeat mechanism for real-time presence

import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js';
import { getDatabase, ref, onDisconnect, serverTimestamp, set, remove, onValue, update } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js';

const firebaseConfig = {
  apiKey: "AIzaSyA7KbB6mlnjZOEH1vpB1oxxTmfPX59mXmQ",
  authDomain: "othello-multi-db60e.firebaseapp.com",
  databaseURL: "https://othello-multi-db60e-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "othello-multi-db60e",
  storageBucket: "othello-multi-db60e.firebasestorage.app",
  messagingSenderId: "529637872871",
  appId: "1:529637872871:web:ced83ae70cad5f01f9be42",
  measurementId: "G-XEFX8706YF"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);
export const auth = getAuth(app);

// Global heartbeat interval
let heartbeatInterval = null;
let currentUserId = null;

/**
 * Initialize anonymous authentication
 * @returns {Promise<User>} Firebase user object
 */
export const initAuth = async () => {
  try {
    const userCredential = await signInAnonymously(auth);
    console.log('✅ Auth initialized:', userCredential.user.uid);
    return userCredential.user;
  } catch (error) {
    console.error('❌ Auth error:', error);
    return null;
  }
};

/**
 * ROBUST HEARTBEAT MECHANISM
 * Updates user presence every 5 seconds
 * Marks user offline on disconnect
 * Shows real-time online player list
 */
export const setupPresence = (userId, displayName) => {
  return new Promise((resolve) => {
    currentUserId = userId;
    const userPresenceRef = ref(db, `online/${userId}`);
    const connectedRef = ref(db, '.info/connected');

    // Listen to Firebase connection state
    onValue(connectedRef, (snapshot) => {
      if (snapshot.val() === true) {
        console.log('🔗 Connected to Firebase');

        // Set up disconnect handler - automatically removes user when they disconnect
        onDisconnect(userPresenceRef).remove();

        // Set user as online with metadata
        const presenceData = {
          online: true,
          displayName: displayName || `Guest_${userId.slice(-4)}`,
          lastSeen: serverTimestamp(),
          connectedAt: serverTimestamp(),
          userAgent: navigator.userAgent.substring(0, 100) // Browser info
        };

        set(userPresenceRef, presenceData)
          .then(() => {
            console.log('✅ Presence set for:', displayName);
            startHeartbeat(userId, displayName);
            resolve(presenceData);
          })
          .catch(err => console.error('❌ Presence error:', err));
      } else {
        console.log('⚠️ Disconnected from Firebase');
      }
    });
  });
};

/**
 * Start heartbeat - updates lastSeen every 5 seconds
 * This ensures real-time tracking of active players
 */
function startHeartbeat(userId, displayName) {
  // Clear existing interval if any
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }

  const userPresenceRef = ref(db, `online/${userId}`);

  // Send heartbeat every 5 seconds
  heartbeatInterval = setInterval(() => {
    update(userPresenceRef, {
      lastSeen: serverTimestamp(),
      online: true
    }).catch(err => console.error('❌ Heartbeat error:', err));
  }, 5000); // Update every 5 seconds

  console.log('💓 Heartbeat started - updating every 5s');
}

/**
 * Stop heartbeat when user manually logs out
 */
export const stopPresence = async () => {
  if (currentUserId) {
    // Clear heartbeat interval
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval);
      heartbeatInterval = null;
    }

    // Remove user from online list
    const userPresenceRef = ref(db, `online/${currentUserId}`);
    await remove(userPresenceRef);
    
    console.log('🛑 Presence stopped for:', currentUserId);
    currentUserId = null;
  }
};

/**
 * Listen to all online users in real-time
 * Automatically filters out stale connections (inactive > 30s)
 */
export const listenToOnlineUsers = (callback) => {
  const onlineRef = ref(db, 'online');
  
  onValue(onlineRef, (snapshot) => {
    const data = snapshot.val() || {};
    const now = Date.now();
    const STALE_THRESHOLD = 30000; // 30 seconds

    // Filter out stale users (haven't sent heartbeat in 30s)
    const activeUsers = {};
    Object.entries(data).forEach(([uid, userData]) => {
      if (userData.lastSeen && (now - userData.lastSeen < STALE_THRESHOLD || userData.lastSeen > now - STALE_THRESHOLD)) {
        activeUsers[uid] = userData;
      } else {
        // Remove stale user
        remove(ref(db, `online/${uid}`)).catch(() => {});
      }
    });

    console.log('👥 Active online users:', Object.keys(activeUsers).length);
    callback(activeUsers);
  });
};

/**
 * Clean up on page unload
 */
window.addEventListener('beforeunload', () => {
  if (currentUserId) {
    // This will trigger the onDisconnect handler
    const userPresenceRef = ref(db, `online/${currentUserId}`);
    remove(userPresenceRef).catch(() => {});
  }
});

console.log('🔥 Firebase module loaded with heartbeat mechanism');'''

print("✅ Created firebase.js with HEARTBEAT mechanism")
print("📄 Size:", len(firebase_js), "bytes")
print("💓 Features:")
print("   - Heartbeat every 5 seconds")
print("   - Auto-remove on disconnect")
print("   - Stale connection cleanup (30s)")
print("   - Real-time online user tracking")
