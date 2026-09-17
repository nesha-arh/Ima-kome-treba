from fastapi import FastAPI, Request, Query, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from typing import Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request, 
    q: Optional[str] = Query(None), 
    category: Optional[str] = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Provera i automatsko kreiranje tabele ako ne postoji
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS oglasi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naslov TEXT NOT NULL,
            kategorija TEXT NOT NULL,
            opis TEXT NOT NULL,
            slika_url TEXT
        )
    """)
    
    query = "SELECT * FROM oglasi WHERE 1=1"
    params = []
    
    if q:
        query += " AND (naslov LIKE ? OR opis LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
        
    if category and category != "":
        query += " AND kategorija = ?"
        params.append(category)
        
    query += " ORDER BY id DESC"
    
    products = cursor.execute(query, params).fetchall()
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "products": products,
        "q": q or "",
        "category": category or ""
    })

@app.post("/add-product")
def add_product(
    naslov: str = Form(...),
    kategorija: str = Form(...),
    opis: str = Form(...),
    slika_url: Optional[str] = Form(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO oglasi (naslov, kategorija, opis, slika_url) VALUES (?, ?, ?, ?)",
        (naslov, kategorija, opis, slika_url or "/static/logo.jpg")
    )
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/", status_code=303)
