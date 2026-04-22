# Huyền Thanh Quote — React + FastAPI

## Cấu trúc project

```
project/
├── backend/          ← Python / FastAPI
│   ├── main.py
│   ├── requirements.txt
│   └── engine/
│       ├── ai_extractor.py   ← copy từ project cũ
│       └── pdf_generator.py  ← copy từ project cũ
│
└── frontend/         ← React / Vite / TypeScript
    ├── src/
    │   ├── App.tsx
    │   ├── App.css
    │   ├── api/client.ts
    │   └── components/
    │       ├── CustomerForm.tsx
    │       ├── ItemsTable.tsx
    │       ├── SummaryBar.tsx
    │       └── UploadPanel.tsx
    ├── index.html
    ├── package.json
    └── vite.config.ts
```

---

## Chạy local (dev)

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Copy engine từ project Streamlit cũ
cp -r /path/to/old/engine ./engine

# Tạo .env
echo "XAI_API_KEY=your_key" > .env
echo "XAI_MODEL=grok-4"    >> .env

uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev     # http://localhost:3000
```

---

## Deploy lên VPS (DigitalOcean / Vultr)

### 1. Chuẩn bị VPS
```bash
# SSH vào VPS
ssh root@your_vps_ip

# Cài Node, Python, Nginx
apt update && apt install -y python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx
```

### 2. Upload code
```bash
# Từ máy local
scp -r project/ root@your_vps_ip:/var/www/huyen-thanh/
```

### 3. Setup Backend
```bash
cd /var/www/huyen-thanh/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Tạo .env
nano .env
# XAI_API_KEY=your_key
# XAI_MODEL=grok-4
```

Tạo service systemd để backend tự chạy khi VPS restart:
```bash
nano /etc/systemd/system/huyen-thanh-api.service
```
```ini
[Unit]
Description=Huyen Thanh FastAPI
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/huyen-thanh/backend
Environment="PATH=/var/www/huyen-thanh/backend/venv/bin"
EnvironmentFile=/var/www/huyen-thanh/backend/.env
ExecStart=/var/www/huyen-thanh/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
systemctl enable huyen-thanh-api
systemctl start huyen-thanh-api
```

### 4. Build Frontend
```bash
cd /var/www/huyen-thanh/frontend

# Trỏ API về domain thật
echo "VITE_API_URL=https://api.yourdomain.com" > .env

npm install
npm run build   # tạo ra folder dist/
```

### 5. Cấu hình Nginx
```bash
nano /etc/nginx/sites-available/huyen-thanh
```
```nginx
# Frontend (app chính)
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/huyen-thanh/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 20M;
    }
}
```
```bash
ln -s /etc/nginx/sites-available/huyen-thanh /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### 6. HTTPS (bắt buộc nếu bán sản phẩm)
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
certbot --nginx -d api.yourdomain.com
```

### 7. Update code sau này
```bash
# Upload code mới
scp -r project/ root@your_vps_ip:/var/www/huyen-thanh/

# Build lại frontend
cd /var/www/huyen-thanh/frontend && npm run build

# Restart backend
systemctl restart huyen-thanh-api
```

---

## Lưu ý
- `engine/` copy nguyên từ Streamlit cũ, không sửa gì
- `images/` (logo, stamp) để trong `backend/images/`
- VPS khuyến nghị tối thiểu: **2GB RAM** (do weasyprint nặng)
