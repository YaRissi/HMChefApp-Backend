from app.services.redis_hander import RedisHandler
import jwt
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
from app.internal.settings import settings
from passlib.context import CryptContext


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
REDIS_HANDLER = RedisHandler()

async def validate_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validiert ein JWT-Token und gibt ein Tupel zurück (ist_gültig, Benutzer_info).

    Args:
        token (str): Das zu validierende JWT-Token.

    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: Gibt zurück, ob das Token gültig ist und die Benutzerinformationen.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        if "exp" in payload and datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc) < datetime.now(datetime.timezone.utc):
            return False, None
        
        return True, payload
    except jwt.PyJWTError:
        return False, None

async def create_token(data: dict, expires_delta: timedelta = None) -> str:
    """Erstellt ein neues JWT-Token.
       Wenn expires_delta None ist, läuft das Token niemals ab.

    Args:
        data (dict): Die Daten, die im Token codiert werden sollen.
        expires_delta (timedelta, optional): Die Dauer, nach der das Token abläuft. Defaults to None.

    Returns:
        str: Das generierte JWT-Token.
    """
    to_encode = data.copy()
    
    if expires_delta is not None:
        expire = datetime.now(datetime.timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


async def register_user(username: str, password: str) -> str:
    """Registriert einen neuen Benutzer und gibt ein Token zurück.

    Args:
        username (str): Der Benutzername.
        password (str): Das Passwort.

    Returns:
        str: Das generierte JWT-Token.
    """
    hashed_password = PWD_CONTEXT.hash(password)
    await REDIS_HANDLER.set_user_password(username, hashed_password)
    
    token = await create_token({"username": username})
    
    return token

async def authenticate_user(username: str, password: str) -> Optional[str]:
    """Authentifiziert einen Benutzer und gibt ein Token zurück.

    Args:
        username (str): Der Benutzername.
        password (str): Das Passwort.

    Returns:
        Optional[str]: Das generierte JWT-Token oder None, wenn die Authentifizierung fehlschlägt.
    """
    user_hashed_password = await REDIS_HANDLER.get_user_password(username)
    
    if user_hashed_password and PWD_CONTEXT.verify(password, user_hashed_password):
        token = await create_token({"username": username})
        return token
    
    return None