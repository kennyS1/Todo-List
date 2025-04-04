from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import aiomysql
from contextlib import asynccontextmanager
from passlib.context import CryptContext

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

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 替换为你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义请求数据模型
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# 依赖注入：获取数据库连接
async def get_db():
    async with app.state.pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur



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


# 登录端点
@app.post("/login")
async def userLogin(user: UserLogin, db=Depends(get_db)):
    try:
        # 查询用户是否存在
        await db.execute("SELECT password FROM users WHERE username = %s", (user.username,))
        result = await db.fetchone()

        if not result:
            raise HTTPException(status_code=400, detail="User not found")

        # 直接比较明文密码（临时解决方案）
        stored_password = result[0]
        if user.password != stored_password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        # 登录成功，返回用户信息
        return {
            "message": "Login successful",
            "username": user.username
        }
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")