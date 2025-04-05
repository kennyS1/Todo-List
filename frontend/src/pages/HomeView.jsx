import React, { useEffect, useState } from "react";

const HomeView = () => {
  const [todos, setTodos] = useState([]);
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  // 加载 todo 列表
  const fetchTodos = async () => {
    try {
      const response = await fetch("http://localhost:8000/todos", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setTodos(data);
    } catch (err) {
      setError("加载失败");
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

    const handleAddTodo = async () => {
    if (!description.trim()) return;

    try {
      const response = await fetch("http://localhost:8000/todos/add", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        const res = await response.json();
        throw new Error(res.detail || "添加失败");
      }

      setDescription(""); // 清空输入框
      fetchTodos(); // 刷新列表
    } catch (err) {
      setError(err.message);
    }
  };


  // ✅ 完成 todo
  const handleComplete = async (id) => {
    await fetch(`http://localhost:8000/todos/${id}/complete`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    fetchTodos(); // 更新页面
  };

  // 🗑 删除 todo
  const handleDelete = async (id) => {
    await fetch(`http://localhost:8000/todos/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    fetchTodos(); // 更新页面
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>📝 我的待办事项</h1>

      <div style={styles.inputWrapper}>
        <input
          type="text"
          placeholder="输入待办事项..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={styles.input}
        />
        <button onClick={handleAddTodo} style={styles.addButton}>
          添加
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={styles.todoList}>
        {todos.map((todo) => (
          <div key={todo.id} style={styles.card}>
            <div style={styles.cardContent}>
              <span style={styles.todoText}>
                {todo.description}{" "}
              </span>
              <span style={styles.complete_tag}>{todo.completed ? "✅" : "❌"}</span>
              <div style={styles.buttonGroup}>
                <button
                  onClick={() => handleComplete(todo.id)}
                  style={styles.completeButton}
                >
                  完成
                </button>
                <button
                  onClick={() => handleDelete(todo.id)}
                  style={styles.deleteButton}
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "600px",
    margin: "0 auto",
    padding: "20px",
    fontFamily: "Arial, sans-serif",
  },
  title: {
    textAlign: "center",
    marginBottom: "20px",
  },
  inputWrapper: {
    display: "flex",
    justifyContent: "center",
    marginBottom: "20px",
  },
  input: {
    flex: 1,
    padding: "10px",
    fontSize: "16px",
    borderRadius: "8px 0 0 8px",
    border: "1px solid #ccc",
  },
  addButton: {
    padding: "10px 16px",
    fontSize: "16px",
    border: "none",
    backgroundColor: "#4CAF50",
    color: "white",
    borderRadius: "0 8px 8px 0",
    cursor: "pointer",
  },
  todoList: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  card: {
    backgroundColor: "#f9f9f9",
    borderRadius: "10px",
    padding: "15px",
    boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
  },
  cardContent: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  todoText: {
    fontSize: "16px",
    fontWeight: "500",
  },
  complete_tag: {
    marginLeft: "auto", // 使该元素靠右对齐
    padding: "15px",
  },
  buttonGroup: {
    display: "flex",
    gap: "10px",
  },
  completeButton: {
    backgroundColor: "#2196F3",
    color: "white",
    border: "none",
    padding: "6px 12px",
    borderRadius: "6px",
    cursor: "pointer",
  },
  deleteButton: {
    backgroundColor: "#f44336",
    color: "white",
    border: "none",
    padding: "6px 12px",
    borderRadius: "6px",
    cursor: "pointer",
  },
};


export default HomeView;
