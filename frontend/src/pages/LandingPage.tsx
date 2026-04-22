import { useNavigate } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import '../layouts/LandingPage.css'; 

export default function LandingPage() {
  const navigate = useNavigate();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // --- ENGINE VẼ MẠNG LƯỚI AI TRÊN CANVAS ---
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let particlesArray: Particle[] = [];
    let animationFrameId: number;

    // Đặt kích thước canvas bằng màn hình
    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Chuột để tạo hiệu ứng tương tác
    const mouse = { x: -1000, y: -1000, radius: 150 };
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.x;
      mouse.y = e.y;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Class Hạt
    class Particle {
      x: number; y: number;
      size: number;
      speedX: number; speedY: number;

      constructor() {
        this.x = Math.random() * canvas!.width;
        this.y = Math.random() * canvas!.height;
        this.size = Math.random() * 2 + 1; // Hạt nhỏ li ti
        this.speedX = Math.random() * 1 - 0.5; // Chuyển động chậm
        this.speedY = Math.random() * 1 - 0.5;
      }
      update() {
        this.x += this.speedX;
        this.y += this.speedY;
        // Bật lại khi chạm viền
        if (this.x > canvas!.width || this.x < 0) this.speedX = -this.speedX;
        if (this.y > canvas!.height || this.y < 0) this.speedY = -this.speedY;
      }
      draw() {
        if (!ctx) return;
        ctx.fillStyle = 'rgba(0, 124, 240, 0.2)'; // Màu xanh AI mờ
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Khởi tạo hạt (Khoảng 70 hạt để không rối mắt)
    const init = () => {
      particlesArray = [];
      for (let i = 0; i < 70; i++) particlesArray.push(new Particle());
    };

    // Vẽ đường nối
    const connect = () => {
      for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
          const dx = particlesArray[a].x - particlesArray[b].x;
          const dy = particlesArray[a].y - particlesArray[b].y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          
          if (distance < 120) { // Khoảng cách nối dây
            ctx!.strokeStyle = `rgba(0, 124, 240, ${0.1 - distance/1200})`; 
            ctx!.lineWidth = 1;
            ctx!.beginPath();
            ctx!.moveTo(particlesArray[a].x, particlesArray[a].y);
            ctx!.lineTo(particlesArray[b].x, particlesArray[b].y);
            ctx!.stroke();
          }
        }
      }
    };

    // Vòng lặp Animation
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
        particlesArray[i].draw();
      }
      connect();
      animationFrameId = requestAnimationFrame(animate);
    };

    init();
    animate();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="lp-root">
      <canvas ref={canvasRef} className="lp-canvas-bg" />
      <div className="lp-grid" />
      <nav className="lp-nav">
        <div className="lp-nav-left">
          <img src="/logo.png" alt="Logo Huyền Thanh" className="lp-logo-img" />
          <span className="lp-brand">HUYỀN THANH AI</span>
        </div>
        <div className="lp-nav-center">
          <a href="#" className="lp-nav-link">Tính năng</a>
          <a href="#" className="lp-nav-link">Hướng dẫn</a>
          <a href="#" className="lp-nav-link">Liên hệ</a>
        </div>
        <div className="lp-nav-right">
          <button className="lp-btn-ghost" onClick={() => navigate('/login')}>Đăng nhập</button>
          <button className="lp-btn-dark" onClick={() => navigate('/login')}>Bắt đầu</button>
        </div>
      </nav>

      <main className="lp-hero">
        <p className="lp-badge">Phiên bản 1.0 — Ra mắt</p>

        <h1 className="lp-hero-title">
          Hệ thống báo giá<br />
          <span className="lp-hero-muted">thế hệ mới.</span>
        </h1>

        <p className="lp-hero-sub">
          Tự động hóa quy trình báo giá với sức mạnh của AI Cloud.<br />
          Nhanh hơn, chính xác hơn, chuyên nghiệp hơn.
        </p>

        <div className="lp-hero-actions">
          <button className="lp-btn-dark lp-btn-lg" onClick={() => navigate('/login')}>
            Bắt đầu ngay
          </button>
          <button className="lp-btn-outline lp-btn-lg">
            Xem tài liệu
          </button>
        </div>
      </main>
    </div>
  );
}