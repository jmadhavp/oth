// firebase.js - FIXED with proper name-based presence

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
let currentDisplayName = null;

/**
 * Initialize anonymous authentication
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
 * Setup or update presence with display name
 * Call this EVERY TIME the display name changes
 */
export const setupPresence = (userId, displayName) => {
  return new Promise((resolve) => {
    currentUserId = userId;
    currentDisplayName = displayName;
    const userPresenceRef = ref(db, `online/${userId}`);
    const connectedRef = ref(db, '.info/connected');

    console.log('🔄 Setting up presence for:', displayName);

    // Listen to Firebase connection state
    onValue(connectedRef, (snapshot) => {
      if (snapshot.val() === true) {
        console.log('🔗 Connected to Firebase');

        // Set up disconnect handler
        onDisconnect(userPresenceRef).remove();

        // Set user as online with metadata
        const presenceData = {
          online: true,
          displayName: displayName,
          lastSeen: serverTimestamp(),
          connectedAt: serverTimestamp(),
          userAgent: navigator.userAgent.substring(0, 100)
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
 * Update display name without reconnecting
 */
export const updatePresenceName = async (userId, newDisplayName) => {
  currentDisplayName = newDisplayName;
  const userPresenceRef = ref(db, `online/${userId}`);
  
  try {
    await update(userPresenceRef, {
      displayName: newDisplayName,
      lastSeen: serverTimestamp()
    });
    console.log('✅ Display name updated to:', newDisplayName);
  } catch (error) {
    console.error('❌ Name update error:', error);
  }
};

/**
 * Start heartbeat - updates every 5 seconds
 */
function startHeartbeat(userId, displayName) {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }

  const userPresenceRef = ref(db, `online/${userId}`);

  heartbeatInterval = setInterval(() => {
    update(userPresenceRef, {
      lastSeen: serverTimestamp(),
      online: true,
      displayName: currentDisplayName || displayName
    }).catch(err => console.error('❌ Heartbeat error:', err));
  }, 5000);

  console.log('💓 Heartbeat started for:', displayName);
}

/**
 * Stop presence
 */
export const stopPresence = async () => {
  if (currentUserId) {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval);
      heartbeatInterval = null;
    }

    const userPresenceRef = ref(db, `online/${currentUserId}`);
    await remove(userPresenceRef);
    
    console.log('🛑 Presence stopped');
    currentUserId = null;
  }
};

/**
 * Listen to all online users
 */
export const listenToOnlineUsers = (callback) => {
  const onlineRef = ref(db, 'online');
  
  onValue(onlineRef, (snapshot) => {
    const data = snapshot.val() || {};
    const now = Date.now();
    const STALE_THRESHOLD = 30000; // 30 seconds

    const activeUsers = {};
    Object.entries(data).forEach(([uid, userData]) => {
      // Check if lastSeen is recent
      const lastSeen = userData.lastSeen || 0;
      const timeDiff = now - lastSeen;
      
      if (timeDiff < STALE_THRESHOLD || lastSeen > now - STALE_THRESHOLD) {
        activeUsers[uid] = userData;
      } else {
        // Remove stale user
        remove(ref(db, `online/${uid}`)).catch(() => {});
      }
    });

    console.log('👥 Active users:', Object.keys(activeUsers).length, Object.values(activeUsers).map(u => u.displayName));
    callback(activeUsers);
  });
};

/**
 * Clean up on page unload
 */
window.addEventListener('beforeunload', () => {
  if (currentUserId) {
    const userPresenceRef = ref(db, `online/${currentUserId}`);
    navigator.sendBeacon && remove(userPresenceRef).catch(() => {});
  }
});

console.log('🔥 Firebase module loaded with heartbeat');