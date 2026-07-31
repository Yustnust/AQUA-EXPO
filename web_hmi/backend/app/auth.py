"""
用户认证与两级权限控制
关联 JIRA: AQEX-54

- JWT 令牌认证（HS256，8 小时有效期）
- 两级角色：操作员 (operator) / 管理员 (admin)
- 用户密码 bcrypt 哈希存储
- 默认账户：operator/Op1234、admin/Ad1234
- 首次部署后强制修改密码
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import aiosqlite
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ============================================================
# 配置
# ============================================================
SECRET_KEY = os.environ.get("WEB_HMI_SECRET_KEY", "aqua-expo-web-hmi-default-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8  # 一个班次

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证方案
bearer_scheme = HTTPBearer(auto_error=False)


# ============================================================
# 角色定义
# ============================================================
ROLE_OPERATOR = "operator"
ROLE_ADMIN = "admin"

# 角色权限矩阵
ROLE_PERMISSIONS = {
    ROLE_OPERATOR: {
        "view": True,           # 查看所有画面
        "alarm_ack": True,      # 报警确认
        "alarm_mute": True,     # 消音
        "trend_view": True,     # 查看趋势曲线
        "start_stop": True,     # 启动/停止/急停（需二次确认）
        "manual_control": False, # 手动控制阀/泵/注射泵
        "param_write": False,   # 参数修改
        "unit_enable": False,   # 单元使能
        "user_manage": False,   # 用户管理
        "system_config": False, # 系统设置
    },
    ROLE_ADMIN: {
        "view": True,
        "alarm_ack": True,
        "alarm_mute": True,
        "trend_view": True,
        "start_stop": True,
        "manual_control": True,
        "param_write": True,
        "unit_enable": True,
        "user_manage": True,
        "system_config": True,
    },
}


# ============================================================
# 默认账户
# ============================================================
DEFAULT_USERS = [
    {"username": "operator", "password": "Op1234", "role": ROLE_OPERATOR, "password_changed": False},
    {"username": "admin",    "password": "Ad1234", "role": ROLE_ADMIN,    "password_changed": False},
]


# ============================================================
# 数据模型
# ============================================================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    expires_in: int  # 秒
    password_changed: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserInfo(BaseModel):
    username: str
    role: str
    password_changed: bool


# ============================================================
# 用户存储
# ============================================================
class UserStore:
    """用户管理 SQLite 存储。"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path

    async def initialize(self):
        """初始化用户表并创建默认账户。"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'operator',
                    password_changed INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT (datetime('now')),
                    updated_at TIMESTAMP DEFAULT (datetime('now'))
                )
            """)
            await db.commit()

            # 创建默认账户（如果不存在）
            for user in DEFAULT_USERS:
                cursor = await db.execute("SELECT id FROM users WHERE username = ?", (user["username"],))
                existing = await cursor.fetchone()
                if not existing:
                    pw_hash = pwd_context.hash(user["password"])
                    await db.execute(
                        "INSERT INTO users (username, password_hash, role, password_changed) VALUES (?, ?, ?, ?)",
                        (user["username"], pw_hash, user["role"], 0),
                    )
                    await db.commit()
                    logger.info("Default user created: %s (%s)", user["username"], user["role"])

        logger.info("User store initialized")

    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户名密码，返回用户信息或 None。"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT username, password_hash, role, password_changed FROM users WHERE username = ?",
                    (username,),
                )
                row = await cursor.fetchone()
                if not row:
                    return None
                if not pwd_context.verify(password, row["password_hash"]):
                    return None
                return {
                    "username": row["username"],
                    "role": row["role"],
                    "password_changed": bool(row["password_changed"]),
                }
        except Exception:
            logger.exception("Auth error")
            return None

    async def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """修改密码。"""
        user = await self.authenticate(username, old_password)
        if not user:
            return False

        new_hash = pwd_context.hash(new_password)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE users SET password_hash = ?, password_changed = 1, updated_at = datetime('now') WHERE username = ?",
                    (new_hash, username),
                )
                await db.commit()
            return True
        except Exception:
            logger.exception("Change password error")
            return False

    async def get_all_users(self) -> list:
        """获取所有用户列表（不含密码哈希）。"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT username, role, password_changed, created_at, updated_at FROM users ORDER BY username"
                )
                return [dict(row) for row in await cursor.fetchall()]
        except Exception:
            logger.exception("Get users error")
            return []

    async def create_user(self, username: str, password: str, role: str) -> bool:
        """创建新用户（仅管理员可调用）。"""
        if role not in (ROLE_OPERATOR, ROLE_ADMIN):
            return False
        pw_hash = pwd_context.hash(password)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO users (username, password_hash, role, password_changed) VALUES (?, ?, ?, 0)",
                    (username, pw_hash, role),
                )
                await db.commit()
            return True
        except Exception:
            logger.exception("Create user error")
            return False

    async def delete_user(self, username: str) -> bool:
        """删除用户（不能删除自己，不能删除最后一个管理员）。"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # 检查是否最后一个管理员
                cursor = await db.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
                row = await cursor.fetchone()
                admin_count = row[0] if row else 0
                if admin_count <= 1:
                    cursor2 = await db.execute("SELECT role FROM users WHERE username = ?", (username,))
                    row2 = await cursor2.fetchone()
                    if row2 and row2[0] == "admin":
                        logger.warning("Cannot delete last admin user")
                        return False

                cursor = await db.execute("DELETE FROM users WHERE username = ?", (username,))
                await db.commit()
                return cursor.rowcount > 0
        except Exception:
            logger.exception("Delete user error")
            return False


# ============================================================
# JWT 令牌工具
# ============================================================
def create_access_token(username: str, role: str, password_changed: bool) -> str:
    """创建 JWT 访问令牌。"""
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": username,
        "role": role,
        "pwd_changed": password_changed,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """解码 JWT 令牌，返回 payload 或 None。"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ============================================================
# 依赖注入：获取当前用户
# ============================================================
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """从请求中提取当前用户信息（FastAPI 依赖注入）。"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "password_changed": payload.get("pwd_changed", False),
    }


def require_role(*roles: str):
    """创建角色依赖——要求当前用户属于指定角色之一。

    用法：
        @app.get("/api/admin-only")
        async def admin_endpoint(user=Depends(require_role("admin"))):
            ...
    """
    async def _check(user: Dict[str, Any] = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(roles)}",
            )
        return user
    return _check


def require_permission(permission: str):
    """创建权限依赖——要求当前用户拥有指定权限。

    用法：
        @app.post("/api/v1/plc/write")
        async def write_var(req, user=Depends(require_permission("param_write"))):
            ...
    """
    async def _check(user: Dict[str, Any] = Depends(get_current_user)):
        perms = ROLE_PERMISSIONS.get(user["role"], {})
        if not perms.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}",
            )
        return user
    return _check


# ============================================================
# 全局用户存储实例
# ============================================================
user_store = UserStore()