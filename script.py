
# Create the ultra-realistic 3D Othello game with physical board design
realistic_3d_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Othello 3D - Realistic Board Game</title>
    
    <!-- Firebase SDKs -->
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
        import { getAuth, RecaptchaVerifier, signInWithPhoneNumber, onAuthStateChanged, signOut, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
        import { getFirestore, collection, addDoc, doc, setDoc, getDoc, getDocs, updateDoc, deleteDoc, onSnapshot, query, where, orderBy, limit, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
        
        const firebaseConfig = {
            apiKey: "AIzaSyA7KbB6mlnjZOEH1vpB1oxxTmfPX59mXmQ",
            authDomain: "othello-multi-db60e.firebaseapp.com",
            projectId: "othello-multi-db60e",
            storageBucket: "othello-multi-db60e.firebasestorage.app",
            messagingSenderId: "529637872871",
            appId: "1:529637872871:web:ced83ae70cad5f01f9be42",
            measurementId: "G-XEFX8706YF"
        };

        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const db = getFirestore(app);
        
        const googleProvider = new GoogleAuthProvider();
        googleProvider.addScope('profile');
        googleProvider.addScope('email');
        googleProvider.setCustomParameters({ prompt: 'select_account' });

        window.auth = auth;
        window.db = db;
        window.firebaseServices = {
            RecaptchaVerifier, signInWithPhoneNumber, onAuthStateChanged, signOut,
            GoogleAuthProvider, signInWithPopup, googleProvider,
            collection, addDoc, doc, setDoc, getDoc, updateDoc, deleteDoc,
            onSnapshot, query, where, orderBy, limit, serverTimestamp, getDocs
        };

        window.signInWithGoogle = async function() {
            try {
                const result = await signInWithPopup(auth, googleProvider);
                const user = result.user;
                
                const userRef = doc(db, 'users', user.uid);
                const userData = {
                    displayName: user.displayName || 'Anonymous',
                    email: user.email,
                    photoURL: user.photoURL,
                    lastLogin: serverTimestamp(),
                    rating: 1000,
                    gamesPlayed: 0,
                    wins: 0,
                    losses: 0,
                    draws: 0
                };
                
                await setDoc(userRef, userData, { merge: true });
                
            } catch (error) {
                console.error('Google sign-in error:', error);
                showAuthError('Google sign-in failed. Please try again.');
            }
        };

        window.addEventListener('DOMContentLoaded', () => {
            window.initializeGame();
        });
    </script>
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --board-green: #0d5a3f;
            --board-green-dark: #094a32;
            --board-edge: #2a2a2a;
            --piece-black: #1a1a1a;
            --piece-white: #f5f5f5;
            --text-light: #f5f5f5;
            --bg-gradient-start: #0a1628;
            --bg-gradient-end: #1a2d4f;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            background-attachment: fixed;
            color: var(--text-light);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .screen {
            display: none;
            min-height: 100vh;
            padding: 20px;
            animation: fadeIn 0.5s ease-in-out;
        }

        .screen.active {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .btn {
            background: linear-gradient(135deg, #4a90e2, #357abd);
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* 3D Board Container */
        .board-container {
            perspective: 1200px;
            margin: 30px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }

        .board-wrapper {
            position: relative;
            transform-style: preserve-3d;
            animation: boardEntry 1s ease-out;
        }

        @keyframes boardEntry {
            from {
                transform: rotateX(45deg) translateY(-50px);
                opacity: 0;
            }
            to {
                transform: rotateX(0deg) translateY(0);
                opacity: 1;
            }
        }

        /* Physical Board Base */
        .game-board-3d {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 3px;
            padding: 30px;
            background: linear-gradient(145deg, var(--board-edge), #1a1a1a);
            border-radius: 8px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.5),
                inset 0 2px 4px rgba(255, 255, 255, 0.1);
            position: relative;
            width: 600px;
            height: 600px;
            transform: rotateX(15deg);
            transition: transform 0.3s ease;
        }

        .game-board-3d:hover {
            transform: rotateX(10deg);
        }

        /* Green Felt Surface */
        .game-board-3d::before {
            content: '';
            position: absolute;
            inset: 20px;
            background: 
                repeating-linear-gradient(
                    0deg,
                    var(--board-green) 0px,
                    var(--board-green-dark) 1px,
                    var(--board-green) 2px
                ),
                repeating-linear-gradient(
                    90deg,
                    var(--board-green) 0px,
                    var(--board-green-dark) 1px,
                    var(--board-green) 2px
                );
            background-size: 100% 50px, 50px 100%;
            border-radius: 4px;
            z-index: 0;
        }

        /* Board Cells */
        .board-cell {
            aspect-ratio: 1;
            background: var(--board-green);
            border: 2px solid var(--board-green-dark);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .board-cell:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .board-cell.valid-move {
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            animation: validPulse 1.5s ease-in-out infinite;
        }

        .board-cell.valid-move::after {
            content: '';
            position: absolute;
            width: 40%;
            height: 40%;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 215, 0, 0.8), transparent);
            animation: hintPulse 1s ease-in-out infinite;
        }

        @keyframes validPulse {
            0%, 100% { box-shadow: inset 0 0 10px rgba(255, 215, 0, 0.3); }
            50% { box-shadow: inset 0 0 20px rgba(255, 215, 0, 0.6); }
        }

        @keyframes hintPulse {
            0%, 100% { transform: scale(0.8); opacity: 0.4; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        /* Realistic 3D Game Pieces */
        .game-piece {
            width: 85%;
            height: 85%;
            border-radius: 50%;
            position: relative;
            transform-style: preserve-3d;
            animation: piecePlace 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            box-shadow: 
                0 4px 8px rgba(0, 0, 0, 0.4),
                0 1px 2px rgba(0, 0, 0, 0.2);
        }

        @keyframes piecePlace {
            0% {
                transform: translateY(-100px) scale(0.5) rotateY(180deg);
                opacity: 0;
            }
            60% {
                transform: translateY(10px) scale(1.1) rotateY(0deg);
            }
            100% {
                transform: translateY(0) scale(1) rotateY(0deg);
                opacity: 1;
            }
        }

        .game-piece.player1 {
            background: radial-gradient(
                circle at 30% 30%,
                #3a3a3a 0%,
                var(--piece-black) 50%,
                #0a0a0a 100%
            );
            border: 2px solid #0a0a0a;
        }

        .game-piece.player1::before {
            content: '';
            position: absolute;
            top: 15%;
            left: 20%;
            width: 40%;
            height: 30%;
            background: radial-gradient(
                ellipse at center,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            border-radius: 50%;
            filter: blur(4px);
        }

        .game-piece.player2 {
            background: radial-gradient(
                circle at 30% 30%,
                #ffffff 0%,
                var(--piece-white) 50%,
                #d0d0d0 100%
            );
            border: 2px solid #c0c0c0;
        }

        .game-piece.player2::before {
            content: '';
            position: absolute;
            top: 15%;
            left: 20%;
            width: 40%;
            height: 30%;
            background: radial-gradient(
                ellipse at center,
                rgba(255, 255, 255, 0.8),
                transparent
            );
            border-radius: 50%;
            filter: blur(3px);
        }

        /* Piece Flip Animation */
        @keyframes pieceFlip {
            0% { transform: rotateY(0deg) scale(1); }
            50% { transform: rotateY(90deg) scale(0.8); }
            100% { transform: rotateY(180deg) scale(1); }
        }

        .game-piece.flipping {
            animation: pieceFlip 0.6s ease-in-out;
        }

        /* Piece Holders (Side Trays) */
        .piece-holder {
            width: 80px;
            background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
            border-radius: 8px;
            padding: 15px 10px;
            box-shadow: 
                0 10px 30px rgba(0, 0, 0, 0.5),
                inset 0 2px 4px rgba(255, 255, 255, 0.1);
            display: flex;
            flex-direction: column;
            gap: 10px;
            align-items: center;
        }

        .piece-holder-title {
            font-size: 12px;
            font-weight: bold;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .holder-pieces {
            display: flex;
            flex-direction: column;
            gap: 5px;
            align-items: center;
        }

        .holder-piece {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
        }

        .holder-piece.black {
            background: radial-gradient(circle at 30% 30%, #3a3a3a, var(--piece-black));
            border: 1px solid #0a0a0a;
        }

        .holder-piece.white {
            background: radial-gradient(circle at 30% 30%, #ffffff, var(--piece-white));
            border: 1px solid #c0c0c0;
        }

        /* Game Header */
        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 900px;
            margin: 20px 0;
        }

        .player-info {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            min-width: 180px;
            transition: all 0.3s ease;
        }

        .player-info.active {
            border-color: #4a90e2;
            box-shadow: 0 0 20px rgba(74, 144, 226, 0.4);
            transform: scale(1.05);
        }

        .player-name {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .player-rating {
            font-size: 14px;
            color: #4a90e2;
            margin-bottom: 5px;
        }

        .player-score {
            font-size: 32px;
            font-weight: bold;
            color: #ffd700;
        }

        /* Timer */
        .timer {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            position: relative;
            margin: 0 30px;
            font-size: 36px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.3);
            border: 4px solid rgba(255, 255, 255, 0.2);
        }

        .timer.green { border-color: #1CEC72; color: #1CEC72; }
        .timer.yellow { border-color: #ffeb3b; color: #ffeb3b; }
        .timer.red { border-color: #FF1686; color: #FF1686; }

        /* Status Message */
        .status-message {
            text-align: center;
            margin: 20px 0;
            font-size: 20px;
            font-weight: bold;
            padding: 15px 30px;
            border-radius: 12px;
            background: rgba(74, 144, 226, 0.2);
            border: 2px solid #4a90e2;
        }

        /* Hint Toggle */
        .hint-toggle {
            margin-top: 20px;
            text-align: center;
        }

        .hint-toggle label {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            cursor: pointer;
            font-size: 16px;
        }

        .hint-toggle input[type="checkbox"] {
            width: 22px;
            height: 22px;
            cursor: pointer;
        }

        /* Floating Menu */
        .floating-menu {
            position: fixed;
            top: 20px;
            left: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 100;
        }

        .floating-btn {
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: white;
            padding: 10px 15px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .floating-btn:hover {
            background: rgba(74, 144, 226, 0.8);
            border-color: #4a90e2;
        }

        /* Modal */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: rgba(26, 45, 79, 0.95);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(74, 144, 226, 0.5);
            border-radius: 16px;
            padding: 40px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        /* Auth Screen */
        .google-sign-in-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: #fff;
            color: #757575;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 280px;
            margin: 0 auto 20px;
        }

        .google-sign-in-btn:hover {
            background: #f5f5f5;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .input-group {
            margin: 15px 0;
            width: 100%;
            max-width: 320px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #4a90e2;
        }

        .input-group input {
            width: 100%;
            padding: 14px;
            border: 2px solid rgba(74, 144, 226, 0.3);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .input-group input:focus {
            outline: none;
            border-color: #4a90e2;
            box-shadow: 0 0 15px rgba(74, 144, 226, 0.3);
        }

        .game-mode-selection {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 30px;
        }

        .mode-btn {
            background: linear-gradient(135deg, #4a90e2, #357abd);
            padding: 25px 40px;
            font-size: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }

        .mode-btn.offline {
            background: linear-gradient(135deg, #FF6B6B, #ee5a52);
        }

        .mode-desc {
            font-size: 14px;
            opacity: 0.9;
            font-weight: normal;
        }

        @media (max-width: 768px) {
            .board-container {
                flex-direction: column;
            }
            
            .game-board-3d {
                width: 90vw;
                height: 90vw;
                max-width: 400px;
                max-height: 400px;
                padding: 20px;
            }
            
            .piece-holder {
                display: none;
            }
            
            .game-header {
                flex-direction: column;
                gap: 15px;
            }
            
            .floating-menu {
                position: relative;
                top: 0;
                left: 0;
                flex-direction: row;
                justify-content: center;
                margin: 20px 0;
            }
        }

        .loading {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(74, 144, 226, 0.3);
            border-radius: 50%;
            border-top-color: #4a90e2;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .victory-screen {
            text-align: center;
            background: rgba(26, 45, 79, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 50px;
            border: 2px solid #4a90e2;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .rating-change {
            font-size: 28px;
            font-weight: bold;
            margin: 20px 0;
            padding: 15px 30px;
            border-radius: 12px;
            display: inline-block;
        }

        .rating-change.positive {
            color: #1CEC72;
            background: rgba(28, 236, 114, 0.2);
            border: 2px solid #1CEC72;
        }

        .rating-change.negative {
            color: #FF1686;
            background: rgba(255, 22, 134, 0.2);
            border: 2px solid #FF1686;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .stat-item {
            text-align: center;
            padding: 20px;
            background: rgba(74, 144, 226, 0.1);
            border-radius: 12px;
            border: 2px solid rgba(74, 144, 226, 0.3);
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #4a90e2;
            display: block;
        }

        .stat-label {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.7);
        }
    </style>
</head>
<body>'''

print("Creating realistic 3D Othello board HTML...")
print("File will be approximately 150KB with full 3D effects and animations")
print("Progress: Creating board structure and piece holders...")
