// firebase.js (uses the firebaseConfig you supplied)
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js';
import { getDatabase } from 'https://www.gstatic.com/firebasejs/9.22.2/firebase-database.js';


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


export const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);