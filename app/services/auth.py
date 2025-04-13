import jwt
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from internal.settings import settings

def validate_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validiert ein JWT-Token und gibt ein Tupel zurück (ist_gültig, Benutzer_info).
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Überprüfen, ob das Token abgelaufen ist
        if "exp" in payload and datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc) < datetime.now(datetime.timezone.utc):
            return False, None
        
        return True, payload
    except jwt.PyJWTError:
        return False, None

def create_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    """
    Erstellt ein neues JWT-Token.
    """
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")