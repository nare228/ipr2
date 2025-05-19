import sys
import os
from fastapi.responses import HTMLResponse
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import getcolvo, html, start

@patch("sqlite3.connect")
def test_getcolvo(mock_connect):
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
    count = getcolvo()
    assert count == 3
    mock_cursor.execute.assert_called_with("SELECT * FROM dataset")

def test_html():
    html_output = html(rows1=[(1, "Задача 1", "Активный", "Описание 1", 3, "2023-01-01"),(2, "Задача 2", "Завершен", "Описание 2", 1, "2023-01-02"),])
    assert "Задача 1" in html_output
    assert "Описание 2" in html_output
    assert "Всего задач:" in html_output
    assert "<form method=\"post\" action=\"/create\">" in html_output
    assert "<button type=\"submit\">Отправить</button>" in html_output

def test_start_with_custom_q():
    test_data = [(1, "Qname", "Qstatus", "Qdesc", 1, "2024-01-01 00:00:00")]
    response = start(q=test_data)
    assert isinstance(response, HTMLResponse)
    assert "Qname" in response.body.decode()
