// firebase.js - Enhanced with authentication and presence system
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js';
import { getDatabase, ref, onDisconnect, serverTimestamp, set } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';
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

// User presence system
export const setupPresence = (userId) => {
  const connectedRef = ref(db, '.info/connected');
  const onlineRef = ref(db, 'online/' + userId);
  const onlineUsersRef = ref(db, 'online');
  
  return new Promise((resolve) => {
    onAuthStateChanged(auth, (user) => {
      if (user) {
        // Add this device to user's connections
        onDisconnect(onlineRef).remove();
        set(onlineRef, {
          online: true,
          lastSeen: serverTimestamp(),
          displayName: localStorage.getItem('playerName') || 'Guest_' + userId.slice(-4)
        });
        resolve(user);
      }
    });
  });
};

// Initialize anonymous auth
export const initAuth = async () => {
  try {
    const userCredential = await signInAnonymously(auth);
    return userCredential.user;
  } catch (error) {
    console.error("Auth error:", error);
    return null;
  }
};