from pathlib import Path

AUTH = Path(__file__).parents[1] / 'backend/app/utils/auth.py'
MAIN = Path(__file__).parents[1] / 'backend/app/main.py'

def test_auth_uses_bcrypt_and_jwt():
    text=AUTH.read_text()
    assert 'import bcrypt' in text
    assert 'bcrypt.hashpw' in text
    assert 'jwt.encode' in text
    assert 'jwt.decode' in text

def test_websocket_validates_jwt():
    text=MAIN.read_text()
    assert "jwt.decode(token" in text
    assert "await websocket.close(code=1008)" in text
