// Firebase Authentication Module
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber, onAuthStateChanged, signOut, GoogleAuthProvider, signInWithPopup } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getFirestore, doc, getDoc, setDoc, serverTimestamp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';

const firebaseConfig = {
    apiKey: "AIzaSyA7KbB6mlnjZOEH1vpB1oxxTmfPX59mXmQ",
    authDomain: "othello-multi-db60e.firebaseapp.com",
    projectId: "othello-multi-db60e",
    storageBucket: "othello-multi-db60e.firebasestorage.app",
    messagingSenderId: "529637872871",
    appId: "1:529637872871:web:ced83ae70cad5f01f9be42",
    measurementId: "G-XEFX8706YF"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const googleProvider = new GoogleAuthProvider();

// User stats constants
const INITIAL_RATING = 1000;
const INITIAL_LEVEL = 1;

// Initialize user data in Firestore
async function initializeUserData(user) {
    const userRef = doc(db, 'users', user.uid);
    const userDoc = await getDoc(userRef);
    
    if (!userDoc.exists()) {
        await setDoc(userRef, {
            uid: user.uid,
            displayName: user.displayName || 'Player',
            rating: INITIAL_RATING,
            level: INITIAL_LEVEL,
            xp: 0,
            wins: 0,
            losses: 0,
            gamesPlayed: 0,
            lastActive: serverTimestamp()
        });
    }
    return userDoc.exists() ? userDoc.data() : await getDoc(userRef).then(doc => doc.data());
}

// Google Sign In
async function signInWithGoogle() {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        const user = result.user;
        await initializeUserData(user);
        showWelcomeScreen();
        return user;
    } catch (error) {
        console.error('Google sign-in error:', error);
        showAuthError('Google sign-in failed. Please try again.');
        throw error;
    }
}

// Phone Authentication
async function sendOTP(phoneNumber, recaptchaContainer) {
    try {
        const recaptchaVerifier = new RecaptchaVerifier(auth, recaptchaContainer, {
            size: 'normal',
            callback: () => {},
            'expired-callback': () => {
                recaptchaVerifier.reset();
            }
        });

        const confirmationResult = await signInWithPhoneNumber(auth, phoneNumber, recaptchaVerifier);
        return confirmationResult;
    } catch (error) {
        console.error('Error sending OTP:', error);
        throw error;
    }
}

async function verifyOTP(confirmationResult, otpCode) {
    try {
        const result = await confirmationResult.confirm(otpCode);
        await initializeUserData(result.user);
        return result.user;
    } catch (error) {
        console.error('Error verifying OTP:', error);
        throw error;
    }
}

// UI Helper Functions
function showAuthError(message) {
    const errorDiv = document.getElementById('auth-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function showWelcomeScreen() {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('welcome-screen').classList.add('active');
}

// Export functions and objects
export {
    auth,
    db,
    signInWithGoogle,
    sendOTP,
    verifyOTP,
    showAuthError,
    showWelcomeScreen,
    initializeUserData
};