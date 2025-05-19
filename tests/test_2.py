import pytest
import sys
import os
import sqlite3
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

@pytest.fixture(autouse=True)
def cleanup():
    conn = sqlite3.connect('fastapidataset.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS dataset")
    conn.commit()
    conn.close()

def test_start():
    response = client.get("/")
    assert response.status_code == 200
    assert "Супер-пупер мега проект" in response.content.decode()
    assert "Всего задач: 0" in response.content.decode()
    assert "<li>" not in response.content.decode()

def test_start2():
    connection = sqlite3.connect("fastapidataset.db")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataset(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            desc TEXT,
            priority INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    cursor.execute("INSERT INTO dataset (name, status, desc, priority) VALUES (?, ?, ?, ?)",("Test", "Активный", "Описание", 5))
    connection.commit()
    connection.close()
    response = client.get("/")
    assert response.status_code == 200
    assert "Test" in response.content.decode()
    assert "Активный" in response.content.decode()
    assert "Описание" in response.content.decode()
    assert "Всего задач: 1" in response.content.decode()

def test_main_page_has_forms():
    response = client.get("/")
    content = response.text
    assert "<form" in content
    assert "Создать задачу" in content
    assert "Удалить задачу" in content
    assert "Найти" in content

def test_screate():
    client.post("/create", data={"field1": "Xу_","options": "Завершен","field3": "Описание","field4": 1}, follow_redirects=False)
    response = client.get("/")
    assert response.status_code == 200
    assert "Xу_" in response.text
    assert "Описание" in response.text

def test_priority():
    for name, priority in [("A", 10), ("B", 1), ("C", 5)]:
        client.post("/create", data={"field1": name,"options": "В ожидании","field3": "Описание","field4": priority}, follow_redirects=False)
    response = client.post("/sorted-by-priority", data={"n": 2})
    assert response.status_code == 200
    text = response.text
    assert "B" in text
    assert "C" in text
    assert "A" not in text

def test_priority_more():
    response = client.post("/sorted-by-priority", data={"n": 100})
    assert response.status_code == 200
    assert "Всего задач" in response.text

def test_del():
    client.post("/create", data={"field1": "Del","options": "Активный","field3": "Удалить эту","field4": 1}, follow_redirects=False)
    assert "Del" in client.get("/").text
    response = client.post("/delete", data={"item_id": 1}, follow_redirects=False)
    assert response.status_code == 303
    assert "Del" not in client.get("/").text

def test_delete_no():
    response = client.post("/delete", data={"item_id": 9999}, follow_redirects=False)
    assert response.status_code == 303

def test_find():
    client.post("/create", data={"field1": "Искать","options": "Активный","field3": "Описание задачи","field4": 1}, follow_redirects=False)
    response = client.post("/find", data={"stroka": "Искать"}, follow_redirects=False)
    assert response.status_code == 200
    assert "Искать" in response.text

def test_find_no():
    response = client.post("/find", data={"stroka": "Нету"}, follow_redirects=False)
    assert response.status_code == 200
    assert "Всего задач" in response.text
