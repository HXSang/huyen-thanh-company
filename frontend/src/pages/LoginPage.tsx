import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../layouts/LoginPage.css'; 

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(''); 
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(''); 
    
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const res = await axios.post('http://localhost:8000/login', formData);
      localStorage.setItem('token', res.data.access_token);
      navigate('/dashboard'); 
    } catch (err) {
      setErrorMsg("Sai tài khoản hoặc mật khẩu. Vui lòng thử lại!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-root">
      <div className="login-card-modern">
        
        <div className="login-header">
          <img src="/logo.png" alt="Logo" className="login-logo" />
          <h2>Đăng nhập</h2>
          <p>Truy cập vào hệ thống báo giá Huyền Thanh AI</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          
          {errorMsg && (
            <div className="login-error">
              ⚠️ {errorMsg}
            </div>
          )}

          <div className="input-group">
            <label>Email doanh nghiệp</label>
            <input 
              type="email" 
              placeholder="admin@huyenthanh.com" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
              disabled={loading}
            />
          </div>

          <div className="input-group">
            <label>Mật khẩu</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? <span className="spinner-small"></span> : "Tiến vào hệ thống"}
          </button>
        </form>

        <div className="login-footer">
          <button className="btn-text" onClick={() => navigate('/')}>
            ← Quay lại trang chủ
          </button>
        </div>

      </div>
    </div>
  );
}