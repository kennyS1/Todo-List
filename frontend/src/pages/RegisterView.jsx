import React, { useState } from 'react';
import '../css/RegisterView.css'; // 假设你有这个 CSS 文件

function RegisterView() {
  // 定义表单状态
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    checkPassword: '',
  });

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

        // 验证逻辑
        if (!formData.username || !formData.password || !formData.checkPassword) {
        alert('Please fill in all fields.');
        return;
        }

        if (formData.password !== formData.checkPassword) {
        alert('Passwords do not match!');
        return;
        }

        try {
        const response = await fetch('http://localhost:8000/register', { // 替换为你的 FastAPI 地址
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
            alert('Registration successful!');
            // 可选：清空表单
            setFormData({ username: '', password: '', checkPassword: '' });
            // 可选：跳转到登录页面（需要 react-router-dom）
            // navigate('/login');
        } else {
            alert(`Registration failed: ${data.detail || 'Unknown error'}`);
        }
        } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while connecting to the server.');
        }
    };



  /***
   * return
   */
  return (
    <div className="card">
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <h1>Register</h1>
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
          <div className="mb-3">
            <label htmlFor="exampleInputCheckPassword" className="form-label">
              Confirm Password
            </label>
            <input
              type="password"
              className="form-control"
              id="exampleInputCheckPassword"
              name="checkPassword"
              value={formData.checkPassword}
              onChange={handleChange}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Register
          </button>
        </form>
      </div>
    </div>
  );
}

export default RegisterView;