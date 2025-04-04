import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // 导入 useNavigate 用于跳转
import '../css/LoginView.css'; // 假设你有这个 CSS 文件

function LoginView() {
  // 定义表单状态
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  // 获取 navigate 函数用于页面跳转
  const navigate = useNavigate();

  // 处理输入变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  // 处理表单提交
  const handleSubmit = async (e) => {
    e.preventDefault(); // 防止页面刷新

    // 验证逻辑：输入非空
    if (!formData.username || !formData.password) {
      alert('Please fill in all fields.');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        alert('Login successful!');
        // 清空表单
        setFormData({ username: '', password: '' });
        // 跳转到主页或其他页面
        navigate('/'); // 假设跳转到主页
      } else {
        alert(`Login failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while connecting to the server.');
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <h1>Login</h1>
          <div className="mb-3">
            <label htmlFor="exampleInputUsername" className="form-label">
              UserName
            </label>
            <input
              type="text"
              className="form-control"
              id="exampleInputUsername"
              name="username"
              value={formData.username}
              onChange={handleChange}
              aria-describedby="usernameHelp"
            />
          </div>
          <div className="mb-3">
            <label htmlFor="exampleInputPassword1" className="form-label">
              Password
            </label>
            <input
              type="password"
              className="form-control"
              id="exampleInputPassword1"
              name="password"
              value={formData.password}
              onChange={handleChange}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Login
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginView;