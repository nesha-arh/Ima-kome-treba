from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import shutil
import os
from datetime import datetime, timedelta

app = FastAPI()

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_url TEXT,
            is_featured INTEGER DEFAULT 0,
            featured_until DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            listing_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            FOREIGN KEY (listing_id) REFERENCES listings (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_id INTEGER NOT NULL,
            rated_user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reviewer_id) REFERENCES users (id),
            FOREIGN KEY (rated_user_id) REFERENCES users (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sponsors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            banner_url TEXT NOT NULL,
            link_url TEXT,
            position TEXT DEFAULT 'top'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="sr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ima kome treba</title>
        <style>
            body {
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='250' height='250'><text x='50%' y='50%' fill='rgba(0,0,0,0.04)' font-size='20' font-weight='bold' font-family='sans-serif' text-anchor='middle' dominant-baseline='middle' transform='rotate(-45, 125, 125)'>ima kome treba</text></svg>");
                background-repeat: repeat;
                background-attachment: fixed;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
                max-width: 800px;
                width: 100%;
                margin-bottom: 25px;
                box-sizing: border-box;
            }
            .sponsor-banner {
                width: 100%;
                max-width: 800px;
                background: #f0f4f8;
                border: 2px dashed #007bff;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
                color: #007bff;
                font-weight: bold;
                box-sizing: border-box;
            }
            h1, h2, h3 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; gap: 10px; }
            input, textarea, select, button {
                padding: 10px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px;
            }
            button { background-color: #4CAF50; color: white; font-weight: bold; cursor: pointer; border: none; }
            button:hover { background-color: #45a049; }
            .auth-box {
                background: #eef6ff;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border: 1px solid #b6d4fe;
            }
            .vip-calculator {
                background: #fff8e1;
                border: 1px solid #ffe082;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
            }
            .vip-calc-details {
                font-weight: bold;
                color: #d84315;
                margin-top: 5px;
            }
            .payment-modal {
                display: none;
                background: #e8f5e9;
                border: 2px solid #66bb6a;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
            }
            .search-box {
                display: flex; gap: 10px; margin-bottom: 20px; width: 100%; max-width: 800px;
            }
            .search-box input { flex: 1; }
            .grid {
                display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 15px; width: 100%; max-width: 800px;
            }
            .card {
                background: white; border-radius: 10px; padding: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between;
                overflow: hidden;
            }
            .card.featured {
                border: 2px solid #ffc107;
                background: #fffdf0;
            }
            .card img { width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
            .card h3 { margin: 0 0 10px 0; color: #222; }
            .card p { margin: 5px 0; color: #555; font-size: 14px; }
            .badge { background: #e0e0e0; padding: 4px 8px; border-radius: 5px; font-size: 12px; align-self: flex-start; }
            .badge-vip { background: #ffc107; color: #000; font-weight: bold; }
            .btn-chat { background-color: #008CBA; margin-top: 10px; }
            .btn-chat:hover { background-color: #007399; }
            
            .chat-container {
                display: none;
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                margin-top: 20px;
                width: 100%;
                max-width: 800px;
                box-sizing: border-box;
            }
            .chat-messages {
                max-height: 250px;
                overflow-y: auto;
                border: 1px solid #eee;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 10px;
                background: #f9f9f9;
            }
            .message-item {
                margin-bottom: 8px;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            .msg-sent { background: #e3f2fd; text-align: right; margin-left: 20%; }
            .msg-received { background: #f1f1f1; text-align: left; margin-right: 20%; }
            .msg-meta { font-size: 11px; color: #888; margin-top: 3px; }

            .sponsors-footer {
                margin-top: 30px;
                padding: 15px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
                width: 100%;
                max-width: 800px;
                text-align: center;
            }
        </style>
    </head>
    <body>

        <div class="sponsor-banner" id="topSponsor">
            📢 Mesto za sponzorski baner / Reklamirajte se ovde!
        </div>

        <div class="container">
            <h1>Ima kome treba</h1>

            <div class="auth-box">
                <div class="user-status" id="userStatus">Niste prijavljeni. Unesite podatke ispod za brzu registraciju/prijavu:</div>
                <form id="authForm" style="flex-direction: row; gap: 10px;">
                    <input type="text" id="regUsername" placeholder="Korisničko ime" required style="flex:1;">
                    <input type="email" id="regEmail" placeholder="Email adresa" required style="flex:1;">
                    <button type="submit">Prijavi se / Registruj</button>
                </form>
            </div>

            <h2>Dodaj novi oglas</h2>
            <form id="addForm">
                <input type="text" id="title" placeholder="Naslov oglasa" required>
                <textarea id="description" placeholder="Opis predmeta" required></textarea>
                <input type="number" step="0.01" id="price" placeholder="Cena (0 za besplatno)" required>
                <input type="text" id="category" placeholder="Kategorija (npr. Nameštaj, Tehnika...)" required>
                <input type="file" id="imageFile" accept="image/*">
                
                <div class="vip-calculator">
                    <label><strong>Opcija isticanja oglasa:</strong></label>
                    <select id="vipOption" onchange="calculateVipPrice()">
                        <option value="0">Standardni besplatni oglas</option>
                        <option value="3">⭐ VIP Istaknut oglas - 3 Dana</option>
                        <option value="7">⭐ VIP Istaknut oglas - 7 Dana (Popularno)</option>
                        <option value="30">⭐ VIP Istaknut oglas - 30 Dana (Najpovoljnije)</option>
                    </select>
                    <div id="vipCalcDisplay" class="vip-calc-details" style="display:none;"></div>
                </div>

                <button type="submit">Objavi oglas</button>
            </form>

            <div class="payment-modal" id="paymentModal">
                <h3>💳 Podaci za uplatu VIP usluge</h3>
                <p id="paymentDetails"></p>
                <button onclick="confirmPayment()">Potvrdi uplatu i aktiviraj</button>
            </div>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Pretraži oglase po reči ili kategoriji...">
            <button onclick="searchListings()">Pretraži</button>
        </div>

        <h2>Aktivni oglasi</h2>
        <div class="grid" id="listingsGrid"></div>

        <div class="chat-container" id="chatContainer">
            <h3 id="chatTitle">Ćaskanje sa prodavcem</h3>
            <div class="chat-messages" id="chatMessages"></div>
            <form id="chatForm" style="flex-direction: row; gap: 10px;">
                <input type="text" id="chatInput" placeholder="Napišite poruku..." required style="flex: 1;">
                <button type="submit">Pošalji</button>
            </form>
        </div>

        <div class="sponsors-footer">
            <h3>Naši Prijatelji & Sponzori</h3>
            <p style="color: #777; font-size: 13px;">Želite da sponzorišete projekat? Kontaktirajte nas za oglasni prostor.</p>
        </div>

        <script>
            let currentUserId = localStorage.getItem('userId') || null;
            let currentUsername = localStorage.getItem('username') || null;
            let activeChatListingId = null;
            let activeChatReceiverId = null;
            let pendingListingData = null;

            function calculateVipPrice() {
                const days = parseInt(document.getElementById('vipOption').value);
                const display = document.getElementById('vipCalcDisplay');
                
                if (days === 0) {
                    display.style.display = 'none';
                    return;
                }

                let price = 0;
                if (days === 3) price = 300;
                else if (days === 7) price = 500;
                else if (days === 30) price = 1500;

                display.style.display = 'block';
                display.innerHTML = `Ukupno za uplatu: <strong>${price} RSD</strong> (VIP pozicija vrha pretrage narednih ${days} dana)`;
            }

            function updateAuthUI() {
                const statusDiv = document.getElementById('userStatus');
                if (currentUserId && currentUsername) {
                    statusDiv.innerHTML = `Prijavljeni ste kao: <strong>${currentUsername}</strong> (ID: ${currentUserId}) <button onclick="logout()" style="padding:3px 8px; margin-left:10px; font-size:12px; background:#e74c3c;">Odjavi se</button>`;
                    document.getElementById('authForm').style.display = 'none';
                } else {
                    statusDiv.innerHTML = 'Niste prijavljeni. Registrujte se ili prijavite za objavljivanje i poruke:';
                    document.getElementById('authForm').style.display = 'flex';
                }
            }

            function logout() {
                localStorage.removeItem('userId');
                localStorage.removeItem('username');
                currentUserId = null;
                currentUsername = null;
                document.getElementById('chatContainer').style.display = 'none';
                updateAuthUI();
            }

            document.getElementById('authForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('regUsername').value;
                const email = document.getElementById('regEmail').value;

                const res = await fetch(`/users/register?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}`, {
                    method: 'POST'
                });
                const data = await res.json();

                if (res.ok) {
                    currentUserId = data.user_id;
                    currentUsername = username;
                    localStorage.setItem('userId', currentUserId);
                    localStorage.setItem('username', currentUsername);
                    updateAuthUI();
                } else {
                    alert(data.detail || "Došlo je do greške pri prijavi.");
                }
            });

            async function renderListings(listings) {
                const grid = document.getElementById('listingsGrid');
                grid.innerHTML = '';
                listings.forEach(item => {
                    const imgTag = item.image_url ? `<img src="/${item.image_url}" alt="Slika">` : '';
                    const isVip = item.is_featured ? 'featured' : '';
                    const vipBadge = item.is_featured ? '<span class="badge badge-vip">⭐ VIP</span> ' : '';
                    
                    const chatBtn = (currentUserId && currentUserId != item.user_id) 
                        ? `<button class="btn-chat" onclick="openChat(${item.id}, ${item.user_id}, '${encodeURIComponent(item.title)}')">💬 Pošalji poruku</button>` 
                        : '';

                    grid.innerHTML += `
                        <div class="card ${isVip}">
                            ${imgTag}
                            <div>
                                ${vipBadge}<span class="badge">${item.category}</span>
                                <h3>${item.title}</h3>
                                <p>${item.description}</p>
                            </div>
                            <div>
                                <p><strong>Cena:</strong> ${item.price === 0 ? 'Besplatno' : item.price + ' RSD'}</p>
                                ${chatBtn}
                            </div>
                        </div>
                    `;
                });
            }

            async function openChat(listingId, sellerId, title) {
                if (!currentUserId) {
                    alert("Morate se prvo prijaviti na vrhu stranice da biste poslali poruku.");
                    return;
                }
                activeChatListingId = listingId;
                activeChatReceiverId = sellerId;
                
                document.getElementById('chatTitle').innerText = `Ćaskanje za oglas: ${decodeURIComponent(title)}`;
                document.getElementById('chatContainer').style.display = 'block';
                document.getElementById('chatContainer').scrollIntoView({ behavior: 'smooth' });
                
                loadMessages();
            }

            async function loadMessages() {
                if (!activeChatListingId || !currentUserId) return;
                const res = await fetch(`/messages/conversation?user1_id=${currentUserId}&user2_id=${activeChatReceiverId}`);
                const data = await res.json();
                const chatBox = document.getElementById('chatMessages');
                chatBox.innerHTML = '';

                data.messages.forEach(msg => {
                    const isMe = msg.sender_id == currentUserId;
                    const cssClass = isMe ? 'msg-sent' : 'msg-received';
                    chatBox.innerHTML += `
                        <div class="message-item ${cssClass}">
                            <div>${msg.content}</div>
                            <div class="msg-meta">${msg.timestamp}</div>
                        </div>
                    `;
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            document.getElementById('chatForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const content = document.getElementById('chatInput').value;
                if (!content || !activeChatListingId) return;

                await fetch(`/messages/send?sender_id=${currentUserId}&receiver_id=${activeChatReceiverId}&listing_id=${activeChatListingId}&content=${encodeURIComponent(content)}`, {
                    method: 'POST'
                });

                document.getElementById('chatInput').value = '';
                loadMessages();
            });

            async function loadListings() {
                const res = await fetch('/listings');
                const data = await res.json();
                renderListings(data.listings);
            }

            async function searchListings() {
                const q = document.getElementById('searchInput').value;
                const res = await fetch(`/listings/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                renderListings(data.results);
            }

            document.getElementById('addForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                if (!currentUserId) {
                    alert("Morate se prvo prijaviti ili registrovati na vrhu stranice!");
                    return;
                }

                const title = document.getElementById('title').value;
                const description = document.getElementById('description').value;
                const price = document.getElementById('price').value;
                const category = document.getElementById('category').value;
                const vipDays = parseInt(document.getElementById('vipOption').value);
                const imageFile = document.getElementById('imageFile').files[0];

                if (vipDays > 0) {
                    let amount = vipDays === 3 ? 300 : (vipDays === 7 ? 500 : 1500);
                    pendingListingData = { title, description, price, category, vipDays, imageFile };
                    
                    document.getElementById('paymentDetails').innerHTML = `
                        Primalac: <strong>Ima Kome Treba d.o.o.</strong><br>
                        Svrha uplate: VIP Isticanje oglasa "${title}" (${vipDays} dana)<br>
                        Iznos: <strong>${amount} RSD</strong><br>
                        Poziv na broj: <strong>VIP-${currentUserId}-${Date.now().toString().slice(-4)}</strong>
                    `;
                    document.getElementById('paymentModal').style.display = 'block';
                    document.getElementById('paymentModal').scrollIntoView({ behavior: 'smooth' });
                    return;
                }

                await submitListing(title, description, price, category, 0, imageFile);
            });

            async function confirmPayment() {
                if (!pendingListingData) return;
                const { title, description, price, category, vipDays, imageFile } = pendingListingData;
                await submitListing(title, description, price, category, vipDays, imageFile);
                document.getElementById('paymentModal').style.display = 'none';
                pendingListingData = null;
                alert("Hvala! Vaš VIP oglas je uspešno aktiviran.");
            }

            async function submitListing(title, description, price, category, vipDays, imageFile) {
                const res = await fetch(`/listings/create?user_id=${currentUserId}&title=${encodeURIComponent(title)}&description=${encodeURIComponent(description)}&price=${price}&category=${encodeURIComponent(category)}&vip_days=${vipDays}`, {
                    method: 'POST'
                });
                const data = await res.json();

                if (imageFile && data.listing_id) {
                    const formData = new FormData();
                    formData.append('file', imageFile);
                    await fetch(`/listings/${data.listing_id}/upload-image`, {
                        method: 'POST',
                        body: formData
                    });
                }

                document.getElementById('addForm').reset();
                calculateVipPrice();
                loadListings();
            }

            updateAuthUI();
            loadListings();
        </script>
    </body>
    </html>
    """

@app.post("/users/register")
def register_user(username: str, email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    existing = cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
    if existing:
        conn.close()
        return {"status": "prijava", "user_id": existing['id'], "message": "Dobrodošli nazad!"}
    
    cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (username, email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {"status": "uspeh", "user_id": user_id}

@app.post("/listings/create")
def create_listing(user_id: int, title: str, description: str, price: float, category: str, vip_days: int = 0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    is_featured = 1 if vip_days > 0 else 0
    featured_until = None
    if is_featured:
        featured_until = (datetime.now() + timedelta(days=vip_days)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        'INSERT INTO listings (user_id, title, description, price, category, image_url, is_featured, featured_until) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (user_id, title, description, price, category, None, is_featured, featured_until)
    )
    conn.commit()
    listing_id = cursor.lastrowid
    conn.close()
    return {"status": "uspeh", "listing_id": listing_id}

@app.post("/listings/{listing_id}/upload-image")
def upload_listing_image(listing_id: int, file: UploadFile = File(...)):
    file_location = f"uploads/{listing_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE listings SET image_url = ? WHERE id = ?', (file_location, listing_id))
    conn.commit()
    conn.close()
    
    return {"status": "uspeh", "image_url": file_location}

@app.get("/listings")
def get_all_listings():
    conn = get_db_connection()
    listings = conn.execute("SELECT * FROM listings ORDER BY is_featured DESC, id DESC").fetchall()
    conn.close()
    return {"listings": [dict(l) for l in listings]}

@app.get("/listings/search")
def search_listings(q: str = None, category: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM listings WHERE 1=1"
    params = []
    if q:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY is_featured DESC, id DESC"
    listings = cursor.execute(query, params).fetchall()
    conn.close()
    return {"results": [dict(l) for l in listings]}

@app.post("/messages/send")
def send_message(sender_id: int, receiver_id: int, listing_id: int, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO messages (sender_id, receiver_id, listing_id, content) VALUES (?, ?, ?, ?)',
        (sender_id, receiver_id, listing_id, content)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return {"status": "uspeh", "message_id": msg_id}

@app.get("/messages/conversation")
def get_conversation(user1_id: int, user2_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    messages = cursor.execute(
        '''SELECT * FROM messages 
           WHERE (sender_id = ? AND receiver_id = ?) 
              OR (sender_id = ? AND receiver_id = ?)
           ORDER BY timestamp ASC''',
        (user1_id, user2_id, user2_id, user1_id)
    ).fetchall()
    conn.close()
    return {"messages": [dict(m) for m in messages]}

@app.post("/sponsors/add")
def add_sponsor(name: str, banner_url: str, link_url: str = None, position: str = "top"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO sponsors (name, banner_url, link_url, position) VALUES (?, ?, ?, ?)',
        (name, banner_url, link_url, position)
    )
    conn.commit()
    sponsor_id = cursor.lastrowid
    conn.close()
    return {"status": "uspeh", "sponsor_id": sponsor_id}

@app.get("/sponsors")
def get_sponsors():
    conn = get_db_connection()
    sponsors = conn.execute("SELECT * FROM sponsors").fetchall()
    conn.close()
    return {"sponsors": [dict(s) for s in sponsors]}
