
# Continue creating the complete HTML with body content and JavaScript
complete_html_part2 = '''
    <!-- Floating Menu -->
    <div id="floating-menu" class="floating-menu" style="display: none;">
        <button class="floating-btn" onclick="showInstructions()">📖 Instructions</button>
        <button class="floating-btn" onclick="quitGame()">🚪 Quit Game</button>
    </div>

    <!-- Auth Screen -->
    <div id="auth-screen" class="screen active">
        <h1 style="font-size: 3.5em; margin-bottom: 20px; text-shadow: 0 0 20px rgba(74, 144, 226, 0.5);">OTHELLO 3D</h1>
        <h2 style="margin-bottom: 50px; color: #4a90e2;">Realistic Multiplayer Board Game</h2>
        
        <div style="text-align: center; max-width: 400px;">
            <h3 style="margin-bottom: 25px;">Sign In</h3>
            
            <button class="google-sign-in-btn" onclick="window.signInWithGoogle()">
                <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg"><path d="M17.64 9.2c0-.63-.06-1.24-.16-1.84H9v3.5h4.84c-.22 1.13-.87 2.08-1.86 2.72v2.26h2.92c1.7-1.57 2.68-3.87 2.68-6.64z" fill="#4285f4"/><path d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.8.54-1.83.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H1.02v2.33C3.19 16.36 5.87 18 9 18z" fill="#34a853"/><path d="M3.96 11.39c-.18-.53-.28-1.1-.28-1.68 0-.58.1-1.15.28-1.68V5.7H1.02A9 9 0 0 0 0 9c0 2.19.78 4.2 2.02 5.74l1.94-3.35z" fill="#fbbc05"/><path d="M9 3.58c2.43 0 4.61.84 6.32 2.44l2.58-2.58C15.66 1.31 12.62 0 9 0 5.87 0 3.19 1.64 1.02 3.99l2.94 2.35C4.68 5.15 6.66 3.58 9 3.58z" fill="#ea4335"/></svg>
                Sign in with Google
            </button>

            <div style="text-align: center; margin: 20px 0;">
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div style="flex-grow: 1; height: 1px; background: rgba(255, 255, 255, 0.3);"></div>
                    <span style="margin: 0 15px; color: rgba(255, 255, 255, 0.7);">OR</span>
                    <div style="flex-grow: 1; height: 1px; background: rgba(255, 255, 255, 0.3);"></div>
                </div>
            </div>

            <h3 style="margin-bottom: 20px;">Phone Authentication</h3>
            
            <div id="phone-input-section">
                <div class="country-select" style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <select id="country-code" style="background: rgba(0, 0, 0, 0.3); color: white; border: 2px solid rgba(74, 144, 226, 0.3); border-radius: 8px; padding: 12px; width: 100%;">
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
                </button>
            </div>
            
            <div id="otp-input-section" style="display: none;">
                <div class="input-group">
                    <label for="otp-code">Enter OTP Code</label>
                    <input type="number" id="otp-code" placeholder="123456" maxlength="6">
                </div>
                
                <button class="btn" id="verify-otp-btn" onclick="verifyOTP()">Verify OTP</button>
                <button class="btn" style="background: gray;" onclick="showPhoneInput()">Back</button>
            </div>
            
            <div id="auth-error" style="color: #FF1686; margin-top: 20px; display: none;"></div>
        </div>
    </div>

    <!-- Main Menu -->
    <div id="main-menu-screen" class="screen">
        <h1 style="font-size: 3.5em; margin-bottom: 20px; text-shadow: 0 0 20px rgba(74, 144, 226, 0.5);">OTHELLO 3D</h1>
        
        <div id="user-welcome" style="margin-bottom: 40px; text-align: center;">
            <div style="font-size: 20px; margin-bottom: 10px;">Welcome back,</div>
            <div id="user-name" style="font-size: 28px; font-weight: bold; color: #4a90e2;">Player</div>
            <div id="user-rating" style="font-size: 18px; color: #ffd700; margin-top: 10px;">⭐ Rating: 1000</div>
        </div>
        
        <div style="display: flex; flex-direction: column; align-items: center; gap: 15px;">
            <button class="btn" style="font-size: 22px; padding: 20px 50px;" onclick="showGameModeSelection()">🎮 Play Game</button>
            <button class="btn" onclick="showProfile()">👤 My Profile</button>
            <button class="btn" onclick="showInstructions()">📖 Instructions</button>
            <button class="btn" style="background: linear-gradient(135deg, #666, #888);" onclick="logout()">🚪 Logout</button>
        </div>
    </div>

    <!-- Game Mode Selection -->
    <div id="game-mode-screen" class="screen">
        <h2 style="margin-bottom: 40px; font-size: 2.5em;">Select Game Mode</h2>
        
        <div class="game-mode-selection">
            <button class="btn mode-btn" onclick="startMatchmaking()">
                🌐 Online Multiplayer
                <span class="mode-desc">Play against players worldwide with ratings</span>
            </button>
            
            <button class="btn mode-btn offline" onclick="startOfflineMode()">
                👥 Local 2-Player
                <span class="mode-desc">Pass & play on same device</span>
            </button>
        </div>
        
        <button class="btn" style="background: gray; margin-top: 30px;" onclick="goToMainMenu()">← Back</button>
    </div>

    <!-- Matchmaking Screen -->
    <div id="matchmaking-screen" class="screen">
        <h2 style="margin-bottom: 30px; font-size: 2.2em;">Finding Opponent...</h2>
        
        <div class="loading" style="margin: 40px auto;"></div>
        
        <div style="text-align: center; margin: 30px;">
            <p style="font-size: 18px;">Searching for a player near your skill level...</p>
            <p style="color: #4a90e2; margin-top: 15px; font-size: 20px;">Your Rating: <span id="matchmaking-rating">1000</span> ⭐</p>
        </div>
        
        <div id="opponent-found" style="display: none; text-align: center; margin-top: 40px;">
            <h3 style="color: #1CEC72; margin-bottom: 20px; font-size: 24px;">Opponent Found! 🎉</h3>
            <div style="background: rgba(0, 0, 0, 0.4); border-radius: 16px; padding: 30px; margin: 30px auto; max-width: 350px; border: 2px solid #4a90e2;">
                <div id="opponent-name" style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">Nova</div>
                <div id="opponent-rating" style="color: #4a90e2; margin-bottom: 10px; font-size: 18px;">⭐ Rating: 1050</div>
                <div id="opponent-stats" style="font-size: 16px; opacity: 0.9;">Win Rate: 65%</div>
            </div>
            <div id="game-countdown" style="font-size: 64px; font-weight: bold; color: #ffd700; margin: 30px 0;">3</div>
        </div>
        
        <button class="btn" style="background: gray;" onclick="cancelMatchmaking()">Cancel</button>
    </div>

    <!-- Game Screen with 3D Board -->
    <div id="game-screen" class="screen">
        <div class="game-header">
            <div id="player1-info" class="player-info">
                <div class="player-name" id="p1-name">You</div>
                <div class="player-rating" id="p1-rating">⭐ 1000</div>
                <div class="player-score" id="p1-score">2</div>
            </div>
            
            <div class="timer" id="game-timer">
                <span id="timer-text">15</span>
            </div>
            
            <div id="player2-info" class="player-info">
                <div class="player-name" id="p2-name">Opponent</div>
                <div class="player-rating" id="p2-rating">⭐ 1000</div>
                <div class="player-score" id="p2-score">2</div>
            </div>
        </div>
        
        <div class="status-message" id="game-status">Your turn - You play as Black</div>
        
        <!-- 3D Board with Side Holders -->
        <div class="board-container">
            <!-- Left Piece Holder (Black) -->
            <div class="piece-holder" id="left-holder">
                <div class="piece-holder-title">Black</div>
                <div class="holder-pieces">
                    <div class="holder-piece black"></div>
                    <div class="holder-piece black"></div>
                    <div class="holder-piece black"></div>
                    <div class="holder-piece black"></div>
                </div>
            </div>
            
            <!-- Main Game Board -->
            <div class="board-wrapper">
                <div class="game-board-3d" id="game-board"></div>
            </div>
            
            <!-- Right Piece Holder (White) -->
            <div class="piece-holder" id="right-holder">
                <div class="piece-holder-title">White</div>
                <div class="holder-pieces">
                    <div class="holder-piece white"></div>
                    <div class="holder-piece white"></div>
                    <div class="holder-piece white"></div>
                    <div class="holder-piece white"></div>
                </div>
            </div>
        </div>
        
        <div class="hint-toggle">
            <label>
                <input type="checkbox" id="show-hints" checked onchange="toggleHints()">
                <span style="font-size: 18px;">💡 Show Move Hints</span>
            </label>
        </div>
    </div>

    <!-- Victory Screen -->
    <div id="victory-screen" class="screen">
        <div class="victory-screen">
            <h2 id="victory-title" style="font-size: 3em; margin-bottom: 30px;">Victory! 🎉</h2>
            
            <div style="font-size: 1.3em; margin: 30px 0;">
                <div style="margin-bottom: 10px;">Final Score:</div>
                <div style="font-size: 2.5em; margin: 15px 0;">
                    <span style="color: #1CEC72;" id="final-p1-score">32</span> - 
                    <span style="color: #FF1686;" id="final-p2-score">32</span>
                </div>
            </div>
            
            <div class="rating-change positive" id="rating-change">+25 Rating</div>
            
            <div style="margin: 40px 0;">
                <div style="font-size: 20px;">New Rating: <span id="new-rating" style="color: #ffd700; font-weight: bold;">1025</span> ⭐</div>
            </div>
            
            <div style="margin-top: 40px;">
                <button class="btn" style="font-size: 20px;" onclick="showGameModeSelection()">Play Again 🎮</button>
                <button class="btn" onclick="goToMainMenu()">Main Menu 🏠</button>
            </div>
        </div>
    </div>

    <!-- Profile Screen -->
    <div id="profile-screen" class="screen">
        <h2 style="margin-bottom: 40px; font-size: 2.5em;">Player Profile</h2>
        
        <div style="text-align: center; max-width: 600px;">
            <div style="font-size: 28px; font-weight: bold; margin-bottom: 15px; color: #4a90e2;" id="profile-name">Player Name</div>
            <div style="font-size: 24px; margin-bottom: 30px; color: #ffd700;" id="profile-rating">⭐ Rating: 1000</div>
            
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
            
            <div style="margin-top: 40px;">
                <button class="btn" onclick="goToMainMenu()">← Back to Menu</button>
            </div>
        </div>
    </div>

    <!-- Instructions Modal -->
    <div id="instructions-modal" class="modal">
        <div class="modal-content">
            <h2 style="margin-bottom: 30px; color: #4a90e2; font-size: 2em;">How to Play Othello</h2>
            
            <div style="text-align: left; max-height: 60vh; overflow-y: auto; padding: 20px;">
                <h3 style="color: #ffd700; margin: 20px 0;">🎯 Objective</h3>
                <p style="line-height: 1.8;">Have the most pieces of your color when the board is full or no more moves are possible.</p>
                
                <h3 style="color: #ffd700; margin: 20px 0;">🎮 How to Play</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Black always starts first</strong></li>
                    <li>Place your piece to <strong>outflank</strong> opponent pieces (sandwich them)</li>
                    <li>All outflanked pieces <strong>flip to your color</strong></li>
                    <li>You must flip at least <strong>one piece</strong> every turn</li>
                    <li>Valid moves show <strong>glowing golden hints</strong> (can be toggled)</li>
                    <li>If no valid moves, turn is <strong>automatically passed</strong></li>
                </ul>
                
                <h3 style="color: #ffd700; margin: 20px 0;">💡 Move Hints</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>Golden glowing squares = Valid moves</li>
                    <li>Pulsing circles = Click to place piece</li>
                    <li>Toggle hints on/off with checkbox</li>
                </ul>
                
                <h3 style="color: #ffd700; margin: 20px 0;">🎮 Game Modes</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>🌐 Online Multiplayer</strong> - Real-time games with rating system</li>
                    <li><strong>👥 Local 2-Player</strong> - Pass device between two players</li>
                </ul>

                <h3 style="color: #ffd700; margin: 20px 0;">⏰ Timer</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>15 seconds per turn in online mode</li>
                    <li>No timer in local 2-player mode</li>
                    <li>Color changes: Green → Yellow → Red</li>
                </ul>
                
                <h3 style="color: #ffd700; margin: 20px 0;">🏆 Strategy Tips</h3>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li><strong>Corners are powerful</strong> - they can't be flipped!</li>
                    <li><strong>Avoid squares next to corners</strong> - they give opponent access</li>
                    <li><strong>Control the center</strong> early in the game</li>
                    <li><strong>Think ahead</strong> - consider opponent's next moves</li>
                </ul>
            </div>
            
            <button class="btn" onclick="hideInstructions()" style="margin-top: 30px; font-size: 18px;">Got it! 👍</button>
        </div>
    </div>'''

print("HTML structure created with 3D board design")
print("Adding JavaScript game logic...")
