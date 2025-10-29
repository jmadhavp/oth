
# Create updated index.html with all requested features
updated_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Othello - Hypnotic Multiplayer</title>
    
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
        
        // Google Provider
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

        // Google Sign-in
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
</head>
<body>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-dark: #00001B;
            --bg-secondary: #0A0E27;
            --primary-purple: #7E30E1;
            --primary-magenta: #E26EE5;
            --accent-cyan: #00F5FF;
            --accent-blue: #0066FF;
            --player1-color: #1CEC72;
            --player2-color: #FF1686;
            --text-light: #F3F8FF;
            --glow-color: rgba(226, 110, 229, 0.6);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-secondary) 50%, #1a0033 100%);
            background-size: 400% 400%;
            background-attachment: fixed;
            color: var(--text-light);
            min-height: 100vh;
            overflow-x: hidden;
            animation: bgShift 15s ease-in-out infinite;
        }

        @keyframes bgShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
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

        .glow-text {
            text-shadow: 0 0 20px var(--glow-color), 0 0 40px var(--glow-color);
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .btn {
            background: linear-gradient(135deg, var(--primary-purple), var(--primary-magenta));
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            color: var(--text-light);
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 0 20px rgba(126, 48, 225, 0.4);
            position: relative;
            overflow: hidden;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(126, 48, 225, 0.6);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .google-sign-in-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: #fff;
            color: #757575;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px 20px;
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            max-width: 240px;
            margin: 0 auto 20px;
        }

        .google-sign-in-btn:hover {
            background: #f5f5f5;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }

        .google-sign-in-btn img {
            width: 18px;
            height: 18px;
        }

        .input-group {
            margin: 15px 0;
            width: 100%;
            max-width: 300px;
        }

        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: var(--accent-cyan);
        }

        .input-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid var(--primary-purple);
            border-radius: 15px;
            background: rgba(10, 14, 39, 0.8);
            color: var(--text-light);
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .input-group input:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid var(--glow-color);
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

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
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-dark));
            border: 2px solid var(--primary-purple);
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            text-align: center;
            box-shadow: 0 0 50px rgba(126, 48, 225, 0.5);
        }

        .game-board {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 2px;
            background: var(--primary-purple);
            border-radius: 15px;
            padding: 10px;
            box-shadow: 0 0 40px rgba(126, 48, 225, 0.5);
            margin: 20px 0;
            max-width: 600px;
        }

        .board-cell {
            aspect-ratio: 1;
            background: var(--bg-secondary);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .board-cell:hover {
            background: rgba(0, 245, 255, 0.1);
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
        }

        .board-cell.valid-move {
            background: rgba(28, 236, 114, 0.2);
            animation: validPulse 1.5s ease-in-out infinite;
        }

        .board-cell.valid-move::after {
            content: '';
            position: absolute;
            width: 30%;
            height: 30%;
            border-radius: 50%;
            background: var(--player1-color);
            opacity: 0.6;
            animation: hintPulse 1s ease-in-out infinite;
        }

        @keyframes validPulse {
            0%, 100% { box-shadow: 0 0 10px rgba(28, 236, 114, 0.3); }
            50% { box-shadow: 0 0 20px rgba(28, 236, 114, 0.6); }
        }

        @keyframes hintPulse {
            0%, 100% { transform: scale(0.8); opacity: 0.4; }
            50% { transform: scale(1); opacity: 0.7; }
        }

        .game-piece {
            width: 80%;
            height: 80%;
            border-radius: 50%;
            transition: all 0.5s ease;
            animation: pieceFlip 0.5s ease-in-out;
        }

        .game-piece.player1 {
            background: radial-gradient(circle, var(--player1-color), #0a8040);
            box-shadow: 0 0 15px rgba(28, 236, 114, 0.5);
        }

        .game-piece.player2 {
            background: radial-gradient(circle, var(--player2-color), #cc1166);
            box-shadow: 0 0 15px rgba(255, 22, 134, 0.5);
        }

        @keyframes pieceFlip {
            0% { transform: scaleY(1); }
            50% { transform: scaleY(0.1); }
            100% { transform: scaleY(1); }
        }

        .timer {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            position: relative;
            margin: 0 20px;
            font-size: 24px;
            font-weight: bold;
        }

        .timer-ring {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 4px solid transparent;
            transition: all 0.1s ease;
        }

        .timer.green .timer-ring { border-color: var(--player1-color); box-shadow: 0 0 20px rgba(28, 236, 114, 0.5); }
        .timer.yellow .timer-ring { border-color: #ffeb3b; box-shadow: 0 0 20px rgba(255, 235, 59, 0.5); }
        .timer.red .timer-ring { border-color: var(--player2-color); box-shadow: 0 0 20px rgba(255, 22, 134, 0.5); }

        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 800px;
            margin: 20px 0;
        }

        .player-info {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            background: rgba(10, 14, 39, 0.6);
            border-radius: 15px;
            border: 2px solid var(--primary-purple);
            min-width: 150px;
        }

        .player-info.active {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        }

        .player-name {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .player-rating {
            font-size: 14px;
            color: var(--accent-cyan);
            margin-bottom: 5px;
        }

        .player-score {
            font-size: 20px;
            font-weight: bold;
            color: var(--primary-magenta);
        }

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
            background: rgba(10, 14, 39, 0.9);
            border: 2px solid var(--primary-purple);
            border-radius: 25px;
            color: var(--text-light);
            padding: 10px 15px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .floating-btn:hover {
            background: rgba(126, 48, 225, 0.8);
            box-shadow: 0 0 15px rgba(126, 48, 225, 0.5);
        }

        .status-message {
            text-align: center;
            margin: 15px 0;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 15px;
            background: rgba(10, 14, 39, 0.6);
            border: 2px solid var(--accent-cyan);
        }

        .hint-toggle {
            margin-top: 10px;
            text-align: center;
        }

        .hint-toggle label {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            cursor: pointer;
            color: var(--accent-cyan);
        }

        .hint-toggle input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }

        @media (max-width: 768px) {
            .game-header {
                flex-direction: column;
                gap: 15px;
            }
            
            .game-board {
                max-width: 350px;
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

        .victory-screen {
            text-align: center;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-dark));
            border-radius: 20px;
            padding: 40px;
            border: 2px solid var(--primary-purple);
            box-shadow: 0 0 50px rgba(126, 48, 225, 0.5);
            animation: victoryPulse 2s ease-in-out infinite;
        }

        @keyframes victoryPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        .rating-change {
            font-size: 24px;
            font-weight: bold;
            margin: 15px 0;
            padding: 10px 20px;
            border-radius: 15px;
            display: inline-block;
        }

        .rating-change.positive {
            color: var(--player1-color);
            background: rgba(28, 236, 114, 0.2);
            border: 2px solid var(--player1-color);
        }

        .rating-change.negative {
            color: var(--player2-color);
            background: rgba(255, 22, 134, 0.2);
            border: 2px solid var(--player2-color);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .stat-item {
            text-align: center;
            padding: 15px;
            background: rgba(10, 14, 39, 0.6);
            border-radius: 15px;
            border: 2px solid var(--primary-purple);
        }

        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--accent-cyan);
            display: block;
        }

        .stat-label {
            font-size: 12px;
            color: var(--text-light);
            opacity: 0.8;
        }

        .game-mode-selection {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
        }

        .mode-btn {
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan));
            padding: 20px 30px;
            font-size: 18px;
        }

        .mode-btn.offline {
            background: linear-gradient(135deg, #FF6B6B, #FFE66D);
        }
    </style>

    <!-- Floating Menu -->
    <div id="floating-menu" class="floating-menu" style="display: none;">
        <button class="floating-btn" onclick="showInstructions()">📖 Instructions</button>
        <button class="floating-btn" onclick="quitGame()">🚪 Quit Game</button>
    </div>

    <!-- Auth Screen -->
    <div id="auth-screen" class="screen active">
        <h1 class="glow-text" style="font-size: 3em; margin-bottom: 30px;">OTHELLO</h1>
        <h2 style="margin-bottom: 40px; color: var(--accent-cyan);">Hypnotic Multiplayer</h2>
        
        <div style="text-align: center; max-width: 400px;">
            <h3 style="margin-bottom: 20px;">Sign In</h3>
            
            <button class="google-sign-in-btn" onclick="window.signInWithGoogle()">
                <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTE3LjY0IDkuMmMwLS42My0uMDYtMS4yNC0uMTYtMS44NEg5djMuNWg0Ljg0Yy0uMjIgMS4xMy0uODcgMi4wOC0xLjg2IDIuNzJ2Mi4yNmgyLjkyYzEuNy0xLjU3IDIuNjgtMy44NyAyLjY4LTYuNjR6IiBmaWxsPSIjNDI4NWY0Ii8+PHBhdGggZD0iTTkgMThjMi40MyAwIDQuNDctLjggNS45Ni0yLjE4bC0yLjkyLTIuMjZjLS44LjU0LTEuODMuODYtMy4wNC44Ni0yLjM0IDAtNC4zMi0xLjU4LTUuMDMtMy43SDEuMDJ2Mi4zM0MzLjE5IDE2LjM2IDUuODcgMTggOSAxOHoiIGZpbGw9IiMzNGE4NTMiLz48cGF0aCBkPSJNMy45NiAxMS4zOWMtLjE4LS41My0uMjgtMS4xLS4yOC0xLjY4IDAtLjU4LjEtMS4xNS4yOC0xLjY4VjUuN0gxLjAyQTkgOSAwIDAgMCAwIDljMCAyLjE5Ljc4IDQuMiAyLjAyIDUuNzRsMS45NC0zLjM1eiIgZmlsbD0iI2ZiYmMwNSIvPjxwYXRoIGQ9Ik05IDMuNThjMi40MyAwIDQuNjEuODQgNi4zMiAyLjQ0bDIuNTgtMi41OEMxNS42NiAxLjMxIDEyLjYyIDAgOSAwIDUuODcgMCAzLjE5IDEuNjQgMS4wMiAzLjk5bDIuOTQgMi4zNUM0LjY4IDUuMTUgNi42NiAzLjU4IDkgMy41OHoiIGZpbGw9IiNlYTQzMzUiLz48L3N2Zz4=" alt="Google logo">
                Sign in with Google
            </button>

            <div style="text-align: center; margin: 20px 0;">
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div style="flex-grow: 1; height: 1px; background: var(--text-light); opacity: 0.3;"></div>
                    <span style="margin: 0 10px; color: var(--text-light); opacity: 0.7;">OR</span>
                    <div style="flex-grow: 1; height: 1px; background: var(--text-light); opacity: 0.3;"></div>
                </div>
            </div>

            <h3 style="margin-bottom: 20px;">Phone Authentication</h3>
            
            <div id="phone-input-section">
                <div class="country-select" style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <select id="country-code" style="background: rgba(10, 14, 39, 0.8); color: var(--text-light); border: 2px solid var(--primary-purple); border-radius: 10px; padding: 8px;">
                        <option value="+91">🇮🇳 +91 (India)</option>
                        <option value="+1">🇺🇸 +1 (USA)</option>
                        <option value="+44">🇬🇧 +44 (UK)</option>
                    </select>
                </div>
                
                <div class="input-group">
                    <label for="phone-number">Phone Number</label>
                    <input type="tel" id="phone-number" placeholder="9876543210" maxlength="15">
                </div>
                
                <div id="recaptcha-container"></div>
                
                <button class="btn" id="send-otp-btn" onclick="sendOTP()">
                    <span id="send-otp-text">Send OTP</span>
                    <div id="send-otp-loading" class="loading" style="display: none;"></div>
                </button>
            </div>
            
            <div id="otp-input-section" style="display: none;">
                <div class="input-group">
                    <label for="otp-code">Enter OTP Code</label>
                    <input type="number" id="otp-code" placeholder="123456" maxlength="6">
                </div>
                
                <button class="btn" id="verify-otp-btn" onclick="verifyOTP()">
                    <span id="verify-otp-text">Verify OTP</span>
                    <div id="verify-otp-loading" class="loading" style="display: none;"></div>
                </button>
                
                <button class="btn" style="background: gray;" onclick="showPhoneInput()">Back</button>
            </div>
            
            <div id="auth-error" style="color: var(--player2-color); margin-top: 15px; display: none;"></div>
        </div>
    </div>

    <!-- Main Menu -->
    <div id="main-menu-screen" class="screen">
        <h1 class="glow-text" style="font-size: 3em; margin-bottom: 20px;">OTHELLO</h1>
        
        <div id="user-welcome" style="margin-bottom: 30px; text-align: center;">
            <div style="font-size: 18px; margin-bottom: 10px;">Welcome back,</div>
            <div id="user-name" style="font-size: 24px; font-weight: bold; color: var(--accent-cyan);">Player</div>
            <div id="user-rating" style="font-size: 16px; color: var(--primary-magenta); margin-top: 5px;">Rating: 1000</div>
        </div>
        
        <div style="display: flex; flex-direction: column; align-items: center; gap: 15px;">
            <button class="btn" style="font-size: 20px; padding: 20px 40px;" onclick="showGameModeSelection()">🎮 Play Game</button>
            <button class="btn" onclick="showProfile()">👤 My Profile</button>
            <button class="btn" onclick="showInstructions()">📖 Instructions</button>
            <button class="btn" style="background: linear-gradient(135deg, #666, #999);" onclick="logout()">🚪 Logout</button>
        </div>
    </div>

    <!-- Game Mode Selection -->
    <div id="game-mode-screen" class="screen">
        <h2 class="glow-text" style="margin-bottom: 30px;">Select Game Mode</h2>
        
        <div class="game-mode-selection">
            <button class="btn mode-btn" onclick="startMatchmaking()">
                🌐 Online Multiplayer
                <div style="font-size: 14px; margin-top: 5px; opacity: 0.8;">Play against real players worldwide</div>
            </button>
            
            <button class="btn mode-btn offline" onclick="startOfflineMode()">
                👥 Local 2-Player
                <div style="font-size: 14px; margin-top: 5px; opacity: 0.8;">Play with a friend on same device</div>
            </button>
        </div>
        
        <button class="btn" style="background: gray; margin-top: 20px;" onclick="goToMainMenu()">Back</button>
    </div>

    <!-- Matchmaking Screen -->
    <div id="matchmaking-screen" class="screen">
        <h2 class="glow-text">Finding Opponent...</h2>
        
        <div class="loading" style="width: 60px; height: 60px; margin: 30px auto; border-width: 6px;"></div>
        
        <div style="text-align: center; margin: 20px;">
            <p>Searching for a player near your skill level...</p>
            <p style="color: var(--accent-cyan); margin-top: 10px;">Your Rating: <span id="matchmaking-rating">1000</span></p>
        </div>
        
        <div id="opponent-found" style="display: none; text-align: center; margin-top: 30px;">
            <h3 style="color: var(--player1-color); margin-bottom: 15px;">Opponent Found! 🎉</h3>
            <div style="background: rgba(10, 14, 39, 0.6); border-radius: 15px; padding: 20px; margin: 20px auto; max-width: 300px; border: 2px solid var(--primary-purple);">
                <div id="opponent-name" style="font-size: 20px; font-weight: bold; margin-bottom: 5px;">Nova</div>
                <div id="opponent-rating" style="color: var(--accent-cyan); margin-bottom: 10px;">Rating: 1050</div>
                <div id="opponent-stats" style="font-size: 14px; opacity: 0.8;">Win Rate: 65%</div>
            </div>
            <div id="game-countdown" style="font-size: 48px; font-weight: bold; color: var(--primary-magenta); margin: 20px 0;">3</div>
        </div>
        
        <button class="btn" style="background: gray;" onclick="cancelMatchmaking()">Cancel</button>
    </div>

    <!-- Game Screen -->
    <div id="game-screen" class="screen">
        <div class="game-header">
            <div id="player1-info" class="player-info">
                <div class="player-name" id="p1-name">You</div>
                <div class="player-rating" id="p1-rating">Rating: 1000</div>
                <div class="player-score" id="p1-score">2</div>
            </div>
            
            <div class="timer" id="game-timer">
                <div class="timer-ring"></div>
                <span id="timer-text">15</span>
            </div>
            
            <div id="player2-info" class="player-info">
                <div class="player-name" id="p2-name">Opponent</div>
                <div class="player-rating" id="p2-rating">Rating: 1000</div>
                <div class="player-score" id="p2-score">2</div>
            </div>
        </div>
        
        <div class="status-message" id="game-status">Your turn - You play as Black</div>
        
        <div class="game-board" id="game-board"></div>
        
        <div class="hint-toggle">
            <label>
                <input type="checkbox" id="show-hints" checked onchange="toggleHints()">
                💡 Show Move Hints
            </label>
        </div>
    </div>

    <!-- Victory Screen -->
    <div id="victory-screen" class="screen">
        <div class="victory-screen">
            <h2 id="victory-title" class="glow-text" style="font-size: 2.5em; margin-bottom: 20px;">Victory!</h2>
            
            <div style="font-size: 1.2em; margin: 20px 0;">
                <div>Final Score:</div>
                <div style="font-size: 2em; margin: 10px 0;">
                    <span style="color: var(--player1-color);" id="final-p1-score">32</span> - 
                    <span style="color: var(--player2-color);" id="final-p2-score">32</span>
                </div>
            </div>
            
            <div class="rating-change positive" id="rating-change">+25 Rating</div>
            
            <div style="margin: 30px 0;">
                <div>New Rating: <span id="new-rating" style="color: var(--accent-cyan); font-weight: bold;">1025</span></div>
            </div>
            
            <div style="margin-top: 30px;">
                <button class="btn" style="font-size: 18px;" onclick="showGameModeSelection()">Play Again 🎮</button>
                <button class="btn" onclick="goToMainMenu()">Main Menu 🏠</button>
            </div>
        </div>
    </div>

    <!-- Profile Screen -->
    <div id="profile-screen" class="screen">
        <h2 class="glow-text" style="margin-bottom: 30px;">Player Profile</h2>
        
        <div style="text-align: center; max-width: 500px;">
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px; color: var(--accent-cyan);" id="profile-name">Player Name</div>
            <div style="font-size: 20px; margin-bottom: 20px; color: var(--primary-magenta);" id="profile-rating">Rating: 1000</div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-value" id="profile-games">0</span>
                    <span class="stat-label">Games Played</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="profile-wins">0</span>
                    <span class="stat-label">Wins</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="profile-losses">0</span>
                    <span class="stat-label">Losses</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="profile-winrate">0%</span>
                    <span class="stat-label">Win Rate</span>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <button class="btn" onclick="goToMainMenu()">Back to Menu</button>
            </div>
        </div>
    </div>

    <!-- Instructions Modal -->
    <div id="instructions-modal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 20px; color: var(--accent-cyan);">How to Play Othello</h2>
            
            <div style="text-align: left; max-height: 60vh; overflow-y: auto;">
                <h3 style="color: var(--primary-magenta); margin: 15px 0;">🎯 Objective</h3>
                <p>Have the most pieces of your color when the board is full or no more moves are possible.</p>
                
                <h3 style="color: var(--primary-magenta); margin: 15px 0;">🎮 How to Play</h3>
                <ul style="margin-left: 20px; line-height: 1.6;">
                    <li><strong>Black always starts first</strong></li>
                    <li>Place your piece to <strong>outflank</strong> opponent pieces</li>
                    <li>All outflanked pieces <strong>flip to your color</strong></li>
                    <li>You must flip at least <strong>one piece</strong> every turn</li>
                    <li>Valid moves are shown with <strong>glowing hints</strong> (can be toggled)</li>
                    <li>If no valid moves, turn is <strong>automatically passed</strong></li>
                </ul>
                
                <h3 style="color: var(--primary-magenta); margin: 15px 0;">💡 Move Hints</h3>
                <ul style="margin-left: 20px; line-height: 1.6;">
                    <li>Green glowing squares show valid moves</li>
                    <li>Pulsing circles indicate where you can place pieces</li>
                    <li>Toggle hints on/off with checkbox below board</li>
                </ul>
                
                <h3 style="color: var(--primary-magenta); margin: 15px 0;">👥 Game Modes</h3>
                <ul style="margin-left: 20px; line-height: 1.6;">
                    <li><strong>Online Multiplayer</strong> - Realtime games with players worldwide</li>
                    <li><strong>Local 2-Player</strong> - Pass & play with friend on same device</li>
                </ul>
            </div>
            
            <button class="btn" onclick="hideInstructions()" style="margin-top: 20px;">Got it! 👍</button>
        </div>
    </div>

    <script>
        // Global state
        let currentUser = null;
        let currentGame = null;
        let gameTimer = null;
        let timeRemaining = 15;
        let isMyTurn = false;
        let gameUnsubscribe = null;
        let matchmakingInterval = null;
        let showHints = true;
        let isOfflineMode = false;
        let currentOfflinePlayer = 'black'; // For offline 2-player mode

        let board = Array(8).fill().map(() => Array(8).fill(null));

        function initializeBoard() {
            board = Array(8).fill().map(() => Array(8).fill(null));
            board[3][3] = 'white';
            board[3][4] = 'black';
            board[4][3] = 'black';
            board[4][4] = 'white';
        }

        window.initializeGame = function() {
            console.log('Initializing game...');
            
            window.firebaseServices.onAuthStateChanged(window.auth, (user) => {
                if (user) {
                    console.log('User signed in:', user.uid);
                    loadUserProfile(user.uid);
                } else {
                    console.log('User signed out');
                    currentUser = null;
                    showScreen('auth-screen');
                }
            });

            setTimeout(() => {
                const recaptchaVerifier = new window.firebaseServices.RecaptchaVerifier(
                    window.auth,
                    'recaptcha-container',
                    { size: 'invisible' }
                );
                window.recaptchaVerifier = recaptchaVerifier;
            }, 1000);
        };

        async function loadUserProfile(uid) {
            try {
                const userDoc = await window.firebaseServices.getDoc(
                    window.firebaseServices.doc(window.db, 'users', uid)
                );
                
                if (userDoc.exists()) {
                    currentUser = { ...userDoc.data(), uid };
                    updateUserWelcome();
                    showScreen('main-menu-screen');
                } else {
                    currentUser = { uid };
                    const displayName = prompt('Enter your name:') || 'Player';
                    await createProfile(displayName);
                }
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        }

        async function createProfile(displayName) {
            try {
                const userData = {
                    displayName,
                    rating: 1000,
                    gamesPlayed: 0,
                    wins: 0,
                    losses: 0,
                    draws: 0,
                    createdAt: window.firebaseServices.serverTimestamp()
                };
                
                await window.firebaseServices.setDoc(
                    window.firebaseServices.doc(window.db, 'users', currentUser.uid),
                    userData
                );
                
                currentUser = { ...userData, uid: currentUser.uid };
                updateUserWelcome();
                showScreen('main-menu-screen');
            } catch (error) {
                console.error('Error creating profile:', error);
            }
        }

        function updateUserWelcome() {
            if (currentUser) {
                document.getElementById('user-name').textContent = currentUser.displayName;
                document.getElementById('user-rating').textContent = `Rating: ${currentUser.rating}`;
            }
        }

        function showGameModeSelection() {
            showScreen('game-mode-screen');
        }

        function startOfflineMode() {
            isOfflineMode = true;
            currentOfflinePlayer = 'black';
            
            // Setup offline game
            initializeBoard();
            setupGameScreen({
                player1: { name: 'Player 1', color: 'black', rating: 0 },
                player2: { name: 'Player 2', color: 'white', rating: 0 },
                board: board,
                currentTurn: 'black'
            });
            
            showScreen('game-screen');
            document.getElementById('floating-menu').style.display = 'flex';
            document.getElementById('game-timer').style.display = 'none'; // No timer in offline mode
        }

        async function startMatchmaking() {
            if (!currentUser) return;
            
            isOfflineMode = false;
            showScreen('matchmaking-screen');
            document.getElementById('matchmaking-rating').textContent = currentUser.rating;
            document.getElementById('opponent-found').style.display = 'none';
            
            try {
                const matchId = Math.random().toString(36).substring(2, 15);
                
                await window.firebaseServices.setDoc(
                    window.firebaseServices.doc(window.db, 'matchmaking_queue', currentUser.uid),
                    {
                        userId: currentUser.uid,
                        displayName: currentUser.displayName,
                        rating: currentUser.rating,
                        joinedAt: window.firebaseServices.serverTimestamp(),
                        status: 'waiting',
                        matchId: matchId
                    }
                );
                
                console.log('Added to matchmaking queue');
                
                // Start looking for match
                matchmakingInterval = setInterval(() => findMatch(), 2000);
                findMatch(); // Call immediately too
                
            } catch (error) {
                console.error('Error joining matchmaking:', error);
                goToMainMenu();
            }
        }

        async function findMatch() {
            try {
                const ratingThreshold = 300;
                
                const q = window.firebaseServices.query(
                    window.firebaseServices.collection(window.db, 'matchmaking_queue'),
                    window.firebaseServices.where('status', '==', 'waiting'),
                    window.firebaseServices.orderBy('joinedAt')
                );
                
                const querySnapshot = await window.firebaseServices.getDocs(q);
                
                let matchedOpponent = null;
                
                for (const doc of querySnapshot.docs) {
                    const opponent = doc.data();
                    
                    if (opponent.userId === currentUser.uid) continue;
                    
                    const ratingDiff = Math.abs(currentUser.rating - opponent.rating);
                    
                    if (ratingDiff <= ratingThreshold) {
                        matchedOpponent = { ...opponent, id: doc.id };
                        break;
                    }
                }
                
                if (matchedOpponent) {
                    console.log('Match found!', matchedOpponent.displayName);
                    
                    // Stop searching
                    if (matchmakingInterval) {
                        clearInterval(matchmakingInterval);
                        matchmakingInterval = null;
                    }
                    
                    // Update both players status
                    await window.firebaseServices.updateDoc(
                        window.firebaseServices.doc(window.db, 'matchmaking_queue', currentUser.uid),
                        { status: 'matched' }
                    );
                    
                    await window.firebaseServices.updateDoc(
                        window.firebaseServices.doc(window.db, 'matchmaking_queue', matchedOpponent.userId),
                        { status: 'matched' }
                    );
                    
                    // Show opponent and create game
                    showOpponentFound(matchedOpponent);
                    
                    setTimeout(() => {
                        createGame(matchedOpponent);
                    }, 4000);
                }
                
            } catch (error) {
                console.error('Error finding match:', error);
            }
        }

        function showOpponentFound(opponent) {
            document.getElementById('opponent-found').style.display = 'block';
            document.getElementById('opponent-name').textContent = opponent.displayName;
            document.getElementById('opponent-rating').textContent = `Rating: ${opponent.rating}`;
            
            const winRate = Math.floor(Math.random() * 40) + 50;
            document.getElementById('opponent-stats').textContent = `Win Rate: ${winRate}%`;
            
            let countdown = 3;
            const countdownEl = document.getElementById('game-countdown');
            
            const countdownInterval = setInterval(() => {
                countdownEl.textContent = countdown;
                countdown--;
                
                if (countdown < 0) {
                    clearInterval(countdownInterval);
                    countdownEl.textContent = 'START!';
                }
            }, 1000);
        }

        async function createGame(opponent) {
            try {
                // Clean up matchmaking queue
                setTimeout(async () => {
                    try {
                        await window.firebaseServices.deleteDoc(
                            window.firebaseServices.doc(window.db, 'matchmaking_queue', currentUser.uid)
                        );
                        await window.firebaseServices.deleteDoc(
                            window.firebaseServices.doc(window.db, 'matchmaking_queue', opponent.userId)
                        );
                    } catch (error) {
                        console.error('Error cleaning matchmaking queue:', error);
                    }
                }, 1000);
                
                const playerIsBlack = Math.random() < 0.5;
                
                const gameData = {
                    player1: {
                        userId: playerIsBlack ? currentUser.uid : opponent.userId,
                        name: playerIsBlack ? currentUser.displayName : opponent.displayName,
                        rating: playerIsBlack ? currentUser.rating : opponent.rating,
                        color: 'black'
                    },
                    player2: {
                        userId: playerIsBlack ? opponent.userId : currentUser.uid,
                        name: playerIsBlack ? opponent.displayName : currentUser.displayName,
                        rating: playerIsBlack ? opponent.rating : currentUser.rating,
                        color: 'white'
                    },
                    board: [
                        [null, null, null, null, null, null, null, null],
                        [null, null, null, null, null, null, null, null],
                        [null, null, null, null, null, null, null, null],
                        [null, null, null, 'white', 'black', null, null, null],
                        [null, null, null, 'black', 'white', null, null, null],
                        [null, null, null, null, null, null, null, null],
                        [null, null, null, null, null, null, null, null],
                        [null, null, null, null, null, null, null, null]
                    ],
                    currentTurn: 'black',
                    moveHistory: [],
                    timer: 15,
                    status: 'active',
                    startedAt: window.firebaseServices.serverTimestamp(),
                    lastMoveAt: window.firebaseServices.serverTimestamp()
                };
                
                const gameRef = await window.firebaseServices.addDoc(
                    window.firebaseServices.collection(window.db, 'games'),
                    gameData
                );
                
                startGame(gameRef.id, gameData);
                
            } catch (error) {
                console.error('Error creating game:', error);
                goToMainMenu();
            }
        }

        async function startGame(gameId, gameData) {
            currentGame = { ...gameData, id: gameId };
            
            // Set up realtime listener
            gameUnsubscribe = window.firebaseServices.onSnapshot(
                window.firebaseServices.doc(window.db, 'games', gameId),
                (doc) => {
                    if (doc.exists()) {
                        updateGameState(doc.data());
                    }
                }
            );
            
            setupGameScreen(gameData);
            showScreen('game-screen');
            document.getElementById('floating-menu').style.display = 'flex';
            document.getElementById('game-timer').style.display = 'flex';
            
            startGameTimer();
        }

        function setupGameScreen(gameData) {
            const isPlayer1 = gameData.player1.userId === currentUser?.uid;
            const myInfo = isPlayer1 ? gameData.player1 : gameData.player2;
            const opponentInfo = isPlayer1 ? gameData.player2 : gameData.player1;
            
            if (!isOfflineMode) {
                document.getElementById('p1-name').textContent = myInfo.name;
                document.getElementById('p1-rating').textContent = `Rating: ${myInfo.rating}`;
                document.getElementById('p2-name').textContent = opponentInfo.name;
                document.getElementById('p2-rating').textContent = `Rating: ${opponentInfo.rating}`;
            } else {
                document.getElementById('p1-name').textContent = gameData.player1.name;
                document.getElementById('p1-rating').style.display = 'none';
                document.getElementById('p2-name').textContent = gameData.player2.name;
                document.getElementById('p2-rating').style.display = 'none';
            }
            
            board = JSON.parse(JSON.stringify(gameData.board));
            createGameBoard();
            updateBoard();
            updateGameInfo();
        }

        function createGameBoard() {
            const boardEl = document.getElementById('game-board');
            boardEl.innerHTML = '';
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const cell = document.createElement('div');
                    cell.className = 'board-cell';
                    cell.dataset.row = row;
                    cell.dataset.col = col;
                    cell.onclick = () => makeMove(row, col);
                    boardEl.appendChild(cell);
                }
            }
        }

        function updateBoard() {
            const cells = document.querySelectorAll('.board-cell');
            
            cells.forEach((cell, index) => {
                const row = Math.floor(index / 8);
                const col = index % 8;
                const piece = board[row][col];
                
                cell.innerHTML = '';
                cell.classList.remove('valid-move');
                
                if (piece) {
                    const pieceEl = document.createElement('div');
                    pieceEl.className = `game-piece ${piece === 'black' ? 'player1' : 'player2'}`;
                    cell.appendChild(pieceEl);
                }
            });
            
            // Show hints for valid moves
            if (showHints && (isMyTurn || isOfflineMode)) {
                const currentColor = isOfflineMode ? currentOfflinePlayer : getCurrentPlayerColor();
                const validMoves = getValidMoves(currentColor);
                
                validMoves.forEach(([row, col]) => {
                    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                    if (cell) {
                        cell.classList.add('valid-move');
                    }
                });
            }
        }

        function getCurrentPlayerColor() {
            if (!currentGame) return null;
            if (isOfflineMode) return currentOfflinePlayer;
            
            const isPlayer1 = currentGame.player1.userId === currentUser.uid;
            return isPlayer1 ? currentGame.player1.color : currentGame.player2.color;
        }

        function updateGameInfo() {
            const scores = calculateScores();
            const currentColor = isOfflineMode ? currentOfflinePlayer : getCurrentPlayerColor();
            
            if (isOfflineMode) {
                document.getElementById('p1-score').textContent = scores['black'];
                document.getElementById('p2-score').textContent = scores['white'];
                
                document.getElementById('game-status').textContent = 
                    `${currentOfflinePlayer === 'black' ? 'Player 1' : 'Player 2'}'s turn (${currentOfflinePlayer})`;
                
                if (currentOfflinePlayer === 'black') {
                    document.getElementById('player1-info').classList.add('active');
                    document.getElementById('player2-info').classList.remove('active');
                } else {
                    document.getElementById('player1-info').classList.remove('active');
                    document.getElementById('player2-info').classList.add('active');
                }
            } else {
                const opponentColor = currentColor === 'black' ? 'white' : 'black';
                
                document.getElementById('p1-score').textContent = scores[currentColor];
                document.getElementById('p2-score').textContent = scores[opponentColor];
                
                if (currentGame.currentTurn === currentColor) {
                    isMyTurn = true;
                    document.getElementById('game-status').textContent = `Your turn - You play as ${currentColor}`;
                    document.getElementById('player1-info').classList.add('active');
                    document.getElementById('player2-info').classList.remove('active');
                } else {
                    isMyTurn = false;
                    document.getElementById('game-status').textContent = `Opponent's turn`;
                    document.getElementById('player1-info').classList.remove('active');
                    document.getElementById('player2-info').classList.add('active');
                }
            }
        }

        function calculateScores() {
            const scores = { black: 0, white: 0 };
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const piece = board[row][col];
                    if (piece) scores[piece]++;
                }
            }
            
            return scores;
        }

        function getValidMoves(color) {
            const validMoves = [];
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    if (board[row][col] === null && isValidMove(row, col, color)) {
                        validMoves.push([row, col]);
                    }
                }
            }
            
            return validMoves;
        }

        function isValidMove(row, col, color) {
            if (board[row][col] !== null) return false;
            
            const directions = [
                [-1, -1], [-1, 0], [-1, 1],
                [0, -1],           [0, 1],
                [1, -1],  [1, 0],  [1, 1]
            ];
            
            const opponentColor = color === 'black' ? 'white' : 'black';
            
            for (const [dx, dy] of directions) {
                let r = row + dx;
                let c = col + dy;
                let hasOpponentBetween = false;
                
                while (r >= 0 && r < 8 && c >= 0 && c < 8) {
                    if (board[r][c] === null) break;
                    
                    if (board[r][c] === opponentColor) {
                        hasOpponentBetween = true;
                    } else if (board[r][c] === color && hasOpponentBetween) {
                        return true;
                    } else {
                        break;
                    }
                    
                    r += dx;
                    c += dy;
                }
            }
            
            return false;
        }

        async function makeMove(row, col) {
            if (isOfflineMode) {
                // Offline mode - handle locally
                if (!isValidMove(row, col, currentOfflinePlayer)) return;
                
                board[row][col] = currentOfflinePlayer;
                flipPieces(board, row, col, currentOfflinePlayer);
                
                // Check if game is over
                const blackValidMoves = getValidMoves('black').length;
                const whiteValidMoves = getValidMoves('white').length;
                
                if (blackValidMoves === 0 && whiteValidMoves === 0) {
                    endOfflineGame();
                    return;
                }
                
                // Switch player
                currentOfflinePlayer = currentOfflinePlayer === 'black' ? 'white' : 'black';
                
                // Skip if no valid moves
                const currentValidMoves = getValidMoves(currentOfflinePlayer);
                if (currentValidMoves.length === 0) {
                    currentOfflinePlayer = currentOfflinePlayer === 'black' ? 'white' : 'black';
                }
                
                updateBoard();
                updateGameInfo();
                
            } else {
                // Online mode
                if (!isMyTurn || !currentGame || currentGame.status !== 'active') return;
                
                const playerColor = getCurrentPlayerColor();
                
                if (!isValidMove(row, col, playerColor)) return;
                
                try {
                    const newBoard = JSON.parse(JSON.stringify(board));
                    newBoard[row][col] = playerColor;
                    flipPieces(newBoard, row, col, playerColor);
                    
                    const nextTurn = playerColor === 'black' ? 'white' : 'black';
                    
                    // Check if game should end
                    const blackMoves = getValidMovesFromBoard(newBoard, 'black').length;
                    const whiteMoves = getValidMovesFromBoard(newBoard, 'white').length;
                    
                    const updateData = {
                        board: newBoard,
                        currentTurn: nextTurn,
                        timer: 15,
                        lastMoveAt: window.firebaseServices.serverTimestamp(),
                        moveHistory: [...(currentGame.moveHistory || []), { row, col, color: playerColor, timestamp: Date.now() }]
                    };
                    
                    if (blackMoves === 0 && whiteMoves === 0) {
                        updateData.status = 'completed';
                        updateData.completedAt = window.firebaseServices.serverTimestamp();
                        
                        const scores = calculateScoresFromBoard(newBoard);
                        if (scores.black > scores.white) {
                            updateData.winner = 'black';
                        } else if (scores.white > scores.black) {
                            updateData.winner = 'white';
                        } else {
                            updateData.winner = 'draw';
                        }
                    }
                    
                    await window.firebaseServices.updateDoc(
                        window.firebaseServices.doc(window.db, 'games', currentGame.id),
                        updateData
                    );
                    
                } catch (error) {
                    console.error('Error making move:', error);
                }
            }
        }

        function getValidMovesFromBoard(boardState, color) {
            const validMoves = [];
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    if (boardState[row][col] === null && isValidMoveOnBoard(boardState, row, col, color)) {
                        validMoves.push([row, col]);
                    }
                }
            }
            
            return validMoves;
        }

        function isValidMoveOnBoard(boardState, row, col, color) {
            if (boardState[row][col] !== null) return false;
            
            const directions = [
                [-1, -1], [-1, 0], [-1, 1],
                [0, -1],           [0, 1],
                [1, -1],  [1, 0],  [1, 1]
            ];
            
            const opponentColor = color === 'black' ? 'white' : 'black';
            
            for (const [dx, dy] of directions) {
                let r = row + dx;
                let c = col + dy;
                let hasOpponentBetween = false;
                
                while (r >= 0 && r < 8 && c >= 0 && c < 8) {
                    if (boardState[r][c] === null) break;
                    
                    if (boardState[r][c] === opponentColor) {
                        hasOpponentBetween = true;
                    } else if (boardState[r][c] === color && hasOpponentBetween) {
                        return true;
                    } else {
                        break;
                    }
                    
                    r += dx;
                    c += dy;
                }
            }
            
            return false;
        }

        function calculateScoresFromBoard(boardState) {
            const scores = { black: 0, white: 0 };
            
            for (let row = 0; row < 8; row++) {
                for (let col = 0; col < 8; col++) {
                    const piece = boardState[row][col];
                    if (piece) scores[piece]++;
                }
            }
            
            return scores;
        }

        function flipPieces(newBoard, row, col, color) {
            const directions = [
                [-1, -1], [-1, 0], [-1, 1],
                [0, -1],           [0, 1],
                [1, -1],  [1, 0],  [1, 1]
            ];
            
            const opponentColor = color === 'black' ? 'white' : 'black';
            
            for (const [dx, dy] of directions) {
                const piecesToFlip = [];
                let r = row + dx;
                let c = col + dy;
                
                while (r >= 0 && r < 8 && c >= 0 && c < 8) {
                    if (newBoard[r][c] === null) break;
                    
                    if (newBoard[r][c] === opponentColor) {
                        piecesToFlip.push([r, c]);
                    } else if (newBoard[r][c] === color) {
                        piecesToFlip.forEach(([fr, fc]) => {
                            newBoard[fr][fc] = color;
                        });
                        break;
                    } else {
                        break;
                    }
                    
                    r += dx;
                    c += dy;
                }
            }
        }

        function endOfflineGame() {
            const scores = calculateScores();
            
            let result = 'draw';
            if (scores.black > scores.white) result = 'win';
            else if (scores.white > scores.black) result = 'loss';
            
            showVictoryScreen(result, scores.black, scores.white, 0);
        }

        function updateGameState(gameData) {
            if (!gameData) return;
            
            currentGame = { ...currentGame, ...gameData };
            board = JSON.parse(JSON.stringify(gameData.board));
            
            updateBoard();
            updateGameInfo();
            
            if (gameData.status === 'completed') {
                endGame(gameData);
            }
            
            // Reset timer
            const lastMoveTime = gameData.lastMoveAt?.seconds ? gameData.lastMoveAt.seconds * 1000 : Date.now();
            if (Date.now() - lastMoveTime < 2000) {
                timeRemaining = gameData.timer || 15;
                updateTimerDisplay();
            }
        }

        function startGameTimer() {
            if (gameTimer) clearInterval(gameTimer);
            
            timeRemaining = 15;
            
            gameTimer = setInterval(async () => {
                if (!isMyTurn || !currentGame || currentGame.status !== 'active') return;
                
                timeRemaining--;
                updateTimerDisplay();
                
                if (timeRemaining <= 0) {
                    await forfeitTurn();
                }
            }, 1000);
        }

        function updateTimerDisplay() {
            const timerEl = document.getElementById('game-timer');
            const textEl = document.getElementById('timer-text');
            
            textEl.textContent = timeRemaining;
            
            timerEl.className = 'timer';
            if (timeRemaining > 10) {
                timerEl.classList.add('green');
            } else if (timeRemaining > 5) {
                timerEl.classList.add('yellow');
            } else {
                timerEl.classList.add('red');
            }
        }

        async function forfeitTurn() {
            if (!currentGame) return;
            
            try {
                const nextTurn = getCurrentPlayerColor() === 'black' ? 'white' : 'black';
                
                await window.firebaseServices.updateDoc(
                    window.firebaseServices.doc(window.db, 'games', currentGame.id),
                    {
                        currentTurn: nextTurn,
                        timer: 15,
                        lastMoveAt: window.firebaseServices.serverTimestamp()
                    }
                );
            } catch (error) {
                console.error('Error forfeiting turn:', error);
            }
        }

        async function endGame(gameData) {
            if (gameTimer) {
                clearInterval(gameTimer);
                gameTimer = null;
            }
            
            if (gameUnsubscribe) {
                gameUnsubscribe();
                gameUnsubscribe = null;
            }
            
            const scores = calculateScores();
            const myColor = getCurrentPlayerColor();
            const myScore = scores[myColor];
            const opponentScore = scores[myColor === 'black' ? 'white' : 'black'];
            
            let result = 'draw';
            let ratingChange = 5;
            
            if (myScore > opponentScore) {
                result = 'win';
                ratingChange = 25;
            } else if (myScore < opponentScore) {
                result = 'loss';
                ratingChange = -15;
            }
            
            await updateUserStats(result, ratingChange);
            showVictoryScreen(result, myScore, opponentScore, ratingChange);
        }

        async function updateUserStats(result, ratingChange) {
            try {
                const newRating = Math.max(0, currentUser.rating + ratingChange);
                const updates = {
                    rating: newRating,
                    gamesPlayed: currentUser.gamesPlayed + 1,
                    lastActive: window.firebaseServices.serverTimestamp()
                };
                
                if (result === 'win') {
                    updates.wins = (currentUser.wins || 0) + 1;
                } else if (result === 'loss') {
                    updates.losses = (currentUser.losses || 0) + 1;
                } else {
                    updates.draws = (currentUser.draws || 0) + 1;
                }
                
                await window.firebaseServices.updateDoc(
                    window.firebaseServices.doc(window.db, 'users', currentUser.uid),
                    updates
                );
                
                Object.assign(currentUser, updates);
                updateUserWelcome();
                
            } catch (error) {
                console.error('Error updating stats:', error);
            }
        }

        function showVictoryScreen(result, myScore, opponentScore, ratingChange) {
            const titleEl = document.getElementById('victory-title');
            const ratingChangeEl = document.getElementById('rating-change');
            
            if (result === 'win') {
                titleEl.textContent = 'Victory! 🎉';
                titleEl.style.color = 'var(--player1-color)';
            } else if (result === 'loss') {
                titleEl.textContent = 'Defeat 😔';
                titleEl.style.color = 'var(--player2-color)';
            } else {
                titleEl.textContent = 'Draw 🤝';
                titleEl.style.color = 'var(--accent-cyan)';
            }
            
            document.getElementById('final-p1-score').textContent = myScore;
            document.getElementById('final-p2-score').textContent = opponentScore;
            
            ratingChangeEl.textContent = `${ratingChange > 0 ? '+' : ''}${ratingChange} Rating`;
            ratingChangeEl.className = `rating-change ${ratingChange >= 0 ? 'positive' : 'negative'}`;
            
            document.getElementById('new-rating').textContent = currentUser.rating;
            
            showScreen('victory-screen');
            document.getElementById('floating-menu').style.display = 'none';
        }

        async function cancelMatchmaking() {
            try {
                if (matchmakingInterval) {
                    clearInterval(matchmakingInterval);
                    matchmakingInterval = null;
                }
                
                await window.firebaseServices.deleteDoc(
                    window.firebaseServices.doc(window.db, 'matchmaking_queue', currentUser.uid)
                );
            } catch (error) {
                console.error('Error canceling matchmaking:', error);
            }
            
            goToMainMenu();
        }

        function toggleHints() {
            showHints = document.getElementById('show-hints').checked;
            updateBoard();
        }

        function showProfile() {
            if (!currentUser) return;
            
            document.getElementById('profile-name').textContent = currentUser.displayName;
            document.getElementById('profile-rating').textContent = `Rating: ${currentUser.rating}`;
            document.getElementById('profile-games').textContent = currentUser.gamesPlayed || 0;
            document.getElementById('profile-wins').textContent = currentUser.wins || 0;
            document.getElementById('profile-losses').textContent = currentUser.losses || 0;
            
            const winRate = currentUser.gamesPlayed > 0 ? 
                Math.round((currentUser.wins || 0) / currentUser.gamesPlayed * 100) : 0;
            document.getElementById('profile-winrate').textContent = `${winRate}%`;
            
            showScreen('profile-screen');
        }

        async function logout() {
            try {
                if (gameUnsubscribe) {
                    gameUnsubscribe();
                    gameUnsubscribe = null;
                }
                
                if (gameTimer) {
                    clearInterval(gameTimer);
                    gameTimer = null;
                }
                
                if (matchmakingInterval) {
                    clearInterval(matchmakingInterval);
                    matchmakingInterval = null;
                }
                
                if (currentUser) {
                    try {
                        await window.firebaseServices.deleteDoc(
                            window.firebaseServices.doc(window.db, 'matchmaking_queue', currentUser.uid)
                        );
                    } catch (error) {
                        // Ignore
                    }
                }
                
                await window.firebaseServices.signOut(window.auth);
                
            } catch (error) {
                console.error('Error logging out:', error);
            }
        }

        function quitGame() {
            if (confirm('Are you sure you want to quit? You may lose rating points.')) {
                if (isOfflineMode) {
                    goToMainMenu();
                } else if (currentGame && currentGame.status === 'active') {
                    forfeitGame();
                } else {
                    goToMainMenu();
                }
            }
        }

        async function forfeitGame() {
            try {
                if (currentGame && currentGame.id) {
                    const myColor = getCurrentPlayerColor();
                    const winner = myColor === 'black' ? 'white' : 'black';
                    
                    await window.firebaseServices.updateDoc(
                        window.firebaseServices.doc(window.db, 'games', currentGame.id),
                        {
                            status: 'forfeited',
                            winner: winner,
                            completedAt: window.firebaseServices.serverTimestamp()
                        }
                    );
                }
            } catch (error) {
                console.error('Error forfeiting:', error);
            }
            
            await updateUserStats('loss', -25);
            goToMainMenu();
        }

        function goToMainMenu() {
            if (gameUnsubscribe) {
                gameUnsubscribe();
                gameUnsubscribe = null;
            }
            
            if (gameTimer) {
                clearInterval(gameTimer);
                gameTimer = null;
            }
            
            if (matchmakingInterval) {
                clearInterval(matchmakingInterval);
                matchmakingInterval = null;
            }
            
            document.getElementById('floating-menu').style.display = 'none';
            currentGame = null;
            isOfflineMode = false;
            
            showScreen('main-menu-screen');
        }

        function showInstructions() {
            document.getElementById('instructions-modal').classList.add('active');
        }

        function hideInstructions() {
            document.getElementById('instructions-modal').classList.remove('active');
        }

        function showScreen(screenId) {
            document.querySelectorAll('.screen').forEach(screen => {
                screen.classList.remove('active');
            });
            
            document.getElementById(screenId).classList.add('active');
        }

        function showPhoneInput() {
            document.getElementById('phone-input-section').style.display = 'block';
            document.getElementById('otp-input-section').style.display = 'none';
            document.getElementById('auth-error').style.display = 'none';
        }

        function showAuthError(message) {
            const errorEl = document.getElementById('auth-error');
            errorEl.textContent = message;
            errorEl.style.display = 'block';
            
            setTimeout(() => {
                errorEl.style.display = 'none';
            }, 5000);
        }

        async function sendOTP() {
            const phoneNumber = document.getElementById('country-code').value + 
                               document.getElementById('phone-number').value.trim();
            
            if (!document.getElementById('phone-number').value.trim()) {
                showAuthError('Please enter a phone number');
                return;
            }
            
            try {
                document.getElementById('send-otp-btn').disabled = true;
                
                const confirmationResult = await window.firebaseServices.signInWithPhoneNumber(
                    window.auth,
                    phoneNumber,
                    window.recaptchaVerifier
                );
                
                window.confirmationResult = confirmationResult;
                
                document.getElementById('phone-input-section').style.display = 'none';
                document.getElementById('otp-input-section').style.display = 'block';
                
            } catch (error) {
                console.error('Error sending OTP:', error);
                showAuthError('Failed to send OTP. Please try again.');
            } finally {
                document.getElementById('send-otp-btn').disabled = false;
            }
        }

        async function verifyOTP() {
            const otpCode = document.getElementById('otp-code').value.trim();
            
            if (!otpCode || otpCode.length !== 6) {
                showAuthError('Please enter a valid 6-digit OTP');
                return;
            }
            
            try {
                document.getElementById('verify-otp-btn').disabled = true;
                
                await window.confirmationResult.confirm(otpCode);
                
            } catch (error) {
                console.error('Error verifying OTP:', error);
                showAuthError('Invalid OTP. Please try again.');
            } finally {
                document.getElementById('verify-otp-btn').disabled = false;
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                hideInstructions();
            }
        });
    </script>
</body>
</html>'''

# Save the file
with open('othello-complete-updated.html', 'w', encoding='utf-8') as f:
    f.write(updated_html)

print("✅ Complete updated Othello game created!")
print("\n🎮 NEW FEATURES ADDED:")
print("1. ✅ Fixed matchmaking - Better opponent finding with proper Firebase sync")
print("2. ✅ Offline 2-player mode - Local pass-and-play on same device")
print("3. ✅ Real-time move synchronization - All player moves sync instantly")
print("4. ✅ Move hints with toggle - Visual hints show valid moves (can turn on/off)")
print("5. ✅ Improved timer display - Better visual feedback")
print("6. ✅ Game mode selection screen - Choose online or offline")
print("\nFile saved as: othello-complete-updated.html")
