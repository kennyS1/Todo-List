import NavBar from './components/NavBar'
import 'bootstrap/dist/css/bootstrap.min.css'; // 导入 Bootstrap CSS
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // 导入 JS（包含 Popper.js）
import RegisterView from './pages/RegisterView';
import HomeView from './pages/HomeView';
import { Routes, Route } from "react-router-dom";
import LoginView from './pages/LoginView';


function App() {

  return (
    <div>
      <NavBar />
      <main >
        <Routes>
          <Route path="/" element={<HomeView />} />
          <Route path="/register" element={<RegisterView />} />
          <Route path="/login" element={<LoginView />} />
        </Routes>
      </main>
    </div>

  )
}

export default App
