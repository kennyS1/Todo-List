from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import aiomysql
from passlib.context import CryptContext
import jwt  # 直接导入 jwt 模块
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

app = FastAPI()

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# database
# 生命周期管理：数据库连接池
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',  # 替换为你的 MySQL 用户名
        password='123456',  # 替换为你的 MySQL 密码
        db='todo_db',  # 替换为你的数据库名
        autocommit=True
    )
    yield
    app.state.pool.close()
    await app.state.pool.wait_closed()

app = FastAPI(lifespan=lifespan)

# JWT配置
SECRET_KEY = "your-secret-key"  # 替换为安全的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 替换为你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TodoItem(BaseModel):
    id: int
    user_id: int
    title: str
    completed: bool
    
    

# 依赖注入：获取数据库连接
async def get_db():
    async with app.state.pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur


# JWT

# 创建访问令牌
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 获取当前用户
async def get_current_user(token: str = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



# api
@app.get("/")
async def home():
    return {"message": "home page"}




# 注册端点
@app.post("/register")
async def userRegister(user: UserRegister, db=Depends(get_db)):
    try:
        # 检查用户名是否已存在
        await db.execute("SELECT username FROM users WHERE username = %s", (user.username,))
        existing_user = await db.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        await db.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, user.password)  # 注意：生产环境中应哈希密码
        )
        return {"message": "Registration successful", "username": user.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# 登录端点（使用明文密码验证）
@app.post("/login")
async def userLogin(user: UserLogin, db=Depends(get_db)):
    try:
        # 查询用户是否存在
        await db.execute("SELECT id, password FROM users WHERE username = %s", (user.username,))
        result = await db.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="User not found")

        user_id, stored_password = result
        # 直接比较明文密码
        if user.password != stored_password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"message": "Login successful", "token": access_token, "user_id": user_id}
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")
