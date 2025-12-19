from datetime import datetime, timedelta
import jwt
import uuid
import pytz
from app.db import get_db_connection
from app.config import Config

# ฟังก์ชันสำหรับได้เวลาปัจจุบันใน timezone ประเทศไทย
def get_current_datetime():
    """ได้เวลาปัจจุบันใน timezone ประเทศไทย (UTC+7)"""
    thailand_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(thailand_tz)

config = Config()

class AuthModel:
    @classmethod
    def generate_tokens(cls, user_email):
        """Generate access and refresh tokens for a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if user exists
            cursor.execute("SELECT * FROM Johnny_user WHERE user_email = ?", (user_email,))
            user = cursor.fetchone()
            if not user:
                return None, None

            # Get user role
            role_id = user[2]  # Assuming role_id is at index 2 based on your schema
            
            # Generate access token
            access_token_payload = {
                'user_email': user_email,
                'role_id': role_id,
                'exp': get_current_datetime() + timedelta(hours=8),  # 8 hours expiration
                'iat': get_current_datetime(),
                'jti': str(uuid.uuid4())
            }
            
            # Generate refresh token
            refresh_token_payload = {
                'user_email': user_email,
                'exp': get_current_datetime() + timedelta(days=7),  # 7 days expiration
                'iat': get_current_datetime(),
                'jti': str(uuid.uuid4())
            }
            
            access_token = jwt.encode(
                access_token_payload,
                config.get('AUTH', 'SECRET_KEY'),
                algorithm='HS256'
            )
            
            refresh_token = jwt.encode(
                refresh_token_payload,
                config.get('AUTH', 'SECRET_KEY'),
                algorithm='HS256'
            )
            
            # Store tokens in database
            token_expire = get_current_datetime() + timedelta(hours=8)
            cursor.execute("""
                UPDATE Johnny_user 
                SET access_token = ?, token_expire = ?, refresh_token = ?, last_login = ?
                WHERE user_email = ?
            """, (access_token, token_expire, refresh_token, get_current_datetime(), user_email))
            conn.commit()
            
            return access_token, refresh_token
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def refresh_access_token(cls, refresh_token):
        """Generate a new access token using a refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token, 
                config.get('AUTH', 'SECRET_KEY'),
                algorithms=['HS256']
            )
            
            user_email = payload.get('user_email')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Check if refresh token is valid in database
                cursor.execute("SELECT * FROM Johnny_user WHERE user_email = ? AND refresh_token = ?", 
                             (user_email, refresh_token))
                user = cursor.fetchone()
                
                if not user:
                    return None
                
                # Generate new access token
                access_token_payload = {
                    'user_email': user_email,
                    'role_id': user[2],  # Assuming role_id is at index 2
                    'exp': get_current_datetime() + timedelta(hours=8),
                    'iat': get_current_datetime(),
                    'jti': str(uuid.uuid4())
                }
                
                access_token = jwt.encode(
                    access_token_payload,
                    config.get('AUTH', 'SECRET_KEY'),
                    algorithm='HS256'
                )
                
                # Update access token in database
                token_expire = get_current_datetime() + timedelta(hours=8)
                cursor.execute("""
                    UPDATE Johnny_user 
                    SET access_token = ?, token_expire = ?
                    WHERE user_email = ?
                """, (access_token, token_expire, user_email))
                conn.commit()
                
                return access_token
            finally:
                cursor.close()
                conn.close()
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def validate_token(cls, token):
        """Validate an access token and return user information"""
        try:
            # Verify token signature and expiration
            payload = jwt.decode(
                token, 
                config.get('AUTH', 'SECRET_KEY'),
                algorithms=['HS256']
            )
            
            user_email = payload.get('user_email')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Check if token is valid in database
                cursor.execute("SELECT * FROM Johnny_user WHERE user_email = ? AND access_token = ?", 
                             (user_email, token))
                user = cursor.fetchone()
                
                if not user:
                    return None
                
                # Check if token is expired in database
                cursor.execute("SELECT token_expire FROM Johnny_user WHERE user_email = ?", (user_email,))
                token_expire = cursor.fetchone()[0]
                
                if token_expire:
                    # Convert token_expire to timezone-aware datetime if it's naive
                    if token_expire.tzinfo is None:
                        # Assume it's in Thailand timezone if it's naive
                        thailand_tz = pytz.timezone('Asia/Bangkok')
                        token_expire = thailand_tz.localize(token_expire)
                    
                    if get_current_datetime() > token_expire:
                        return None
                
                return {
                    'user_email': user_email,
                    'role_id': payload.get('role_id')
                }
            finally:
                cursor.close()
                conn.close()
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @classmethod
    def get_user_permissions(cls, role_id):
        """Get permissions for a role"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_role WHERE role_id = ?", (role_id,))
            role = cursor.fetchone()
            
            if not role:
                return {}
            
            # Convert role data to dictionary
            columns = [column[0] for column in cursor.description]
            role_dict = dict(zip(columns, role))
            
            # Extract permissions
            permissions = {
                'allow_create': role_dict.get('allow_create', 0) == 1,
                'allow_pickup': role_dict.get('allow_pickup', 0) == 1,
                'allow_change': role_dict.get('allow_change', 0) == 1,
                'allow_setting': role_dict.get('allow_setting', 0) == 1,
                'allow_report': role_dict.get('allow_report', 0) == 1,
                'allow_user_manage': role_dict.get('allow_user_manage', 0) == 1
            }
            
            return permissions
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def login(cls, email, password):
        """Authenticate a user and return tokens"""
        # In a real system, you would verify password here
        # For this implementation, we'll just check if user exists
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_user WHERE user_email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                return None, None
            
            # Generate tokens
            access_token, refresh_token = cls.generate_tokens(email)
            
            return access_token, refresh_token
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def logout(cls, user_email):
        """Invalidate user tokens"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Johnny_user 
                SET access_token = NULL, refresh_token = NULL
                WHERE user_email = ?
            """, (user_email,))
            conn.commit()
            return True
        except:
            return False
        finally:
            cursor.close()
            conn.close()

    # @classmethod
    # def get_approver_by_email(cls, user_email):
    #     """Is approver by email"""
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute("SELECT is_approver FROM Johnny_user WHERE user_email = ?", (user_email,))
    #         row = cursor.fetchone()
    #         if row:
    #             return row  # Return the raw row or map to an object
    #         return None
    #     finally:
    #         cursor.close()
    #         conn.close()