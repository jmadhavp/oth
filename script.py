
# Create the complete, fixed, and enhanced files with heartbeat mechanism

# 1. Fixed index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Othello Multiplayer - Enhanced</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <header>
      <div>
        <h1>🎮 Othello Multiplayer</h1>
        <p id="status">Connecting...</p>
        <p id="onlineCount">👥 Online: 0</p>
      </div>
    </header>
    
    <div id="controls">
      <div id="lobby">
        <h3>🎯 Join Game</h3>
        <input type="text" id="playerName" placeholder="Your name" maxlength="20" />
        <div style="display:flex;gap:8px;margin-top:8px">
          <button id="createRoom">Create Room</button>
          <button id="randomJoin">Quick Match</button>
        </div>
        <button id="refreshRooms" style="width:100%;margin-top:8px">🔄 Refresh Lobby</button>
        <div id="roomsList"></div>
      </div>
      
      <div id="onlinePlayersList" style="min-width:240px;background:rgba(255,255,255,0.03);padding:12px;border-radius:12px">
        <h3>👥 Online Players</h3>
        <div id="onlineUsers">Loading...</div>
      </div>
    </div>
    
    <div id="roomLink" class="hidden">
      <p>📎 Room ID: <strong id="roomId"></strong></p>
      <button id="copyLink">Copy Link</button>
      <button id="leaveRoom" style="background:#ef4444">Leave Room</button>
    </div>
    
    <div id="gameArea">
      <div id="boardContainer">
        <canvas id="board" width="640" height="640"></canvas>
      </div>
      
      <div id="side">
        <div id="gameInfo">
          <p id="turnInfo">Turn: Black</p>
          <p id="players">Players: Waiting...</p>
          <p id="timer">Timer: --:--</p>
        </div>
        
        <div id="gameSettings">
          <label>
            <input type="checkbox" id="moveTimerToggle" checked>
            Enable Move Timer (30s)
          </label>
        </div>
        
        <div id="chat">
          <h4>💬 Chat</h4>
          <div id="chatLog"></div>
          <input type="text" id="chatInput" placeholder="Type message..." maxlength="200" />
        </div>
      </div>
    </div>
  </main>
  
  <!-- Sound effects -->
  <audio id="sndPlace" src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBgoKDg4SFhYaHh4iJiYqLi4yNjY6Pj5CRkZKTk5SVlZaXl5iZmZqbm5ydnZ6fn6ChoaKjo6Slpaanpqmpqaqrq6ytrK2trq6vr7CwsbGxsrOztLS1tba2t7i4uLm5urq7u7y8vb2+vr+/wMDBwcHCw8PDxMXFxsbHyMjJyczMzc3Oz8/Q0dHR0tLT09TV1NXW1tfY2Nna2tvc3N3e3d7f3+Dg4eHi4uPj5OTl5eXm5+fo6Ojp6urr6+zs7e3u7u/v8PDx8fLy8/P09PT19fb29/f4+Pn5+vr7+/z8/f3+/v//AAEBAgIDAwQEBQUGBgcHCAgJCQoKCwsMDA0NDg4PDxAQEREREhMTFBQVFRYWFxcYGBkZGRobGxwcHR0eHh8fICAgISIiIyMkJCUlJiYnJygpKCkqKisrLCwtLS4uLy8wMDExMTIzMzQ0NTU2Njc3ODg5OTo6Ozs8PD09Pj4/P0BAQUFCQkNDRERFRUZGR0dISElJSkpLS0xMTU1OTk9PUFBRU1JTVFRVVVZWVldYWFlZWlpbXFxdXV5eX19gYGFhYmJjY2RkZWVmZmdnaGhpaWpqa2tsbG1tbm5vb3BwcXFycnNzdHR1dXZ2d3d4eHl5enp7e3x8fX1+fn9/gICBgYKCg4OEhIWFhoaHh4iIiYmKiouLjIyNjY6Oj4+QkJGRkpKTk5SUlZWWlpeXmJiZmZqam5ucnJ2dnp6fn6CgoaGioqOjpKSlpaampqenqKipqaqqq6usrK2trq6vr7CwsbGysrOztLS1tba2t7e4uLm5urq7u7y8vb2+vr+/wMDBwcLCw8PExMXFxsbHx8jIycnKysvLzMzNzc7Oz8/Q0NHR0tLT09TU1dXW1tfX2NjZ2dra29vc3N3d3t7f3+Dg4eHi4uPj5OTl5ebn5+jo6enq6uvr7Ozt7e7u7+/w8PHx8vLz8/T09fX29vf3+Pj5+fr6+/v8/P39/v7//w==" preload="auto"></audio>
  
  <script type="module" src="./firebase.js"></script>
  <script type="module" src="./main.js"></script>
</body>
</html>'''

print("✅ Created complete index.html")
print("📄 Size:", len(index_html), "bytes")
