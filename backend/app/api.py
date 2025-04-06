from fastapi import FastAPI, HTTPException, Depends, status, Security
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import aiomysql
from passlib.context import CryptContext
import jwt  # 直接导入 jwt 模块
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError  # 修复 JWTError 未定义的问题
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# 替代 oauth2_scheme
bearer_scheme = HTTPBearer()

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
    allow_origins=["*"],  # 替换为你的前端地址
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

class TodoCreate(BaseModel):
    description: str
    
    

# 依赖注入：获取数据库连接
async def get_db():
    async with app.state.pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur


# JWT

# 创建访问令牌
def create_access_token(user_id: int, expires_delta: timedelta):
    to_encode = {"user_id": user_id, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db=Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        await db.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = await db.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return {"user_id": user[0], "username": user[1]}
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# 查询正在登录的userid的todos
@app.get("/todos")
async def get_todos(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    try:
        user_id = current_user["user_id"]
        await db.execute(
            "SELECT id, description, completed FROM todos WHERE user_id = %s",
            (user_id,)
        )
        todos = await db.fetchall()
        return [
            {
                "id": row[0],
                "description": row[1],
                "completed": row[2]
            }
            for row in todos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch todos: {str(e)}")

# 切换完成状态
@app.put("/todos/{todo_id}/complete")
async def toggle_complete(todo_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    try:
        await db.execute("SELECT completed FROM todos WHERE id = %s AND user_id = %s", (todo_id, current_user["user_id"]))
        result = await db.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Todo not found")

        current_status = result[0]
        new_status = not current_status
        await db.execute("UPDATE todos SET completed = %s WHERE id = %s", (new_status, todo_id))
        return {"message": "Todo updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

# 删除
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, current_user=Depends(get_current_user), db=Depends(get_db)):
    try:
        await db.execute("DELETE FROM todos WHERE id = %s AND user_id = %s", (todo_id, current_user["user_id"]))
        return {"message": "Todo deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")




@app.post("/todos/add")
async def add_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    try:
        user_id = current_user["user_id"]  # ✅ 从 token 解析 user_id
        await db.execute(
            "INSERT INTO todos (user_id, description, completed) VALUES (%s, %s, %s)",
            (user_id, todo.description, False)
        )
        return {"message": "Todo added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add todo: {str(e)}")





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
        # 查询用户
        await db.execute("SELECT id, password FROM users WHERE username = %s", (user.username,))
        result = await db.fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="User not found")

        user_id, stored_password = result
        if user.password != stored_password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        # 生成 Token 时存 `user_id`
        access_token = create_access_token(
            user_id=user_id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"message": "Login successful", "token": access_token, "user_id": user_id}
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")
