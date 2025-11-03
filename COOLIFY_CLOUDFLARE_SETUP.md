# Deployment Guide: Coolify + Cloudflare Tunnel

## Setup Anda (Current Configuration)

- **Platform:** Coolify
- **Domain:** backend-openbo.devmosel.com
- **Cloudflare Tunnel:** Port 80 → Server
- **Backend:** Flask running on port 5000

## 🔧 Langkah Setup

### 1. Coolify Configuration

#### A. Port Mapping di Coolify

1. Login ke Coolify Dashboard
2. Pilih service **backend-openbo**
3. Settings → Ports & Volumes
4. **Port Mapping:**
   ```
   Container Port: 5000
   Public Port: 80 (atau auto-assign)
   ```
5. Save & Redeploy

#### B. Environment Variables di Coolify

Masukkan environment variables berikut di Coolify:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-random-secret>
DEBUG=False

# Database Configuration
DB_HOST=<your-db-host>
DB_PORT=3306
DB_USER=openbo
DB_PASSWORD=<your-db-password>
DB_NAME=openbo_db

# DATABASE_URL (alternative)
DATABASE_URL=mysql+pymysql://openbo:<password>@<db-host>:3306/openbo_db

# JWT Configuration
JWT_SECRET_KEY=<generate-random-secret>
JWT_ACCESS_TOKEN_EXPIRES=3600

# CORS Configuration
CORS_ORIGINS=https://your-frontend-domain.com

# Server Configuration
PORT=5000
PYTHONUNBUFFERED=1
```

**Generate Secret Keys:**
```powershell
# Run di terminal lokal
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### 2. Cloudflare Tunnel Configuration

#### Option A: Via Cloudflare Dashboard (Recommended)

1. **Login ke Cloudflare Zero Trust:**
   - https://one.dash.cloudflare.com/

2. **Navigate to Tunnels:**
   - Access → Tunnels → Your Tunnel

3. **Configure Public Hostname:**
   ```
   Subdomain: backend-openbo
   Domain: devmosel.com
   Service:
     Type: HTTP
     URL: localhost:5000  ← PENTING: Port 5000, bukan 80!
   ```

4. **Advanced Settings (Optional):**
   - Enable WebSocket: Yes
   - HTTP Host Header: backend-openbo.devmosel.com
   - Origin Server Name: backend-openbo.devmosel.com

#### Option B: Via Config File

Jika menggunakan `cloudflared` config file:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /path/to/<tunnel-id>.json

ingress:
  - hostname: backend-openbo.devmosel.com
    service: http://localhost:5000
    originRequest:
      connectTimeout: 30s
      noTLSVerify: false
      httpHostHeader: backend-openbo.devmosel.com
  
  - service: http_status:404
```

**Restart cloudflared:**
```bash
# Windows
Restart-Service cloudflared

# Linux
sudo systemctl restart cloudflared
```

### 3. Coolify Build & Deploy

#### A. Dockerfile (Already configured)

File `Dockerfile` sudah siap untuk Coolify.

#### B. Deploy via Git (Recommended)

1. **Commit & Push:**
   ```powershell
   git add .
   git commit -m "Coolify deployment configuration"
   git push origin main
   ```

2. **Coolify akan auto-deploy** jika `auto_deploy: true`

#### C. Manual Deploy

Di Coolify Dashboard:
1. Service → backend-openbo
2. Click **"Restart/Redeploy"**
3. Monitor logs

### 4. Database Setup di Coolify

#### Option A: Coolify Managed Database

1. **Create Database Service:**
   - Service Type: MySQL/MariaDB
   - Version: 11.2 (atau latest)
   - Database Name: openbo_db
   - Username: openbo
   - Password: <generate-secure-password>

2. **Connect to Database:**
   ```
   DB_HOST=<coolify-db-service-name>
   DB_PORT=3306
   ```

#### Option B: External Database

Jika database sudah ada di server lain:
```env
DB_HOST=<external-db-ip-or-domain>
DB_PORT=3306
DB_USER=openbo
DB_PASSWORD=<password>
DB_NAME=openbo_db
```

### 5. Migration & Seeding

**Option A: Automatic (via Dockerfile ENTRYPOINT)**

Dockerfile sudah configured untuk auto-run migration:
```dockerfile
CMD python migrate.py && python seed.py && python run.py
```

**Option B: Manual (via Coolify Console)**

1. Coolify Dashboard → Service → Console
2. Run commands:
   ```bash
   python migrate.py
   python seed.py
   ```

## 🧪 Testing Deployment

### 1. Health Check
```powershell
curl https://backend-openbo.devmosel.com/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### 2. Test Authentication
```powershell
curl -X POST https://backend-openbo.devmosel.com/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email": "admin@openbo.com", "password": "Admin123!"}'
```

### 3. Test API Endpoints
```powershell
# Get spaces
curl https://backend-openbo.devmosel.com/api/spaces

# Get floors
curl https://backend-openbo.devmosel.com/api/floors
```

## 📊 Monitoring

### 1. Coolify Logs

```
Service → Logs → Real-time
```

Filter by:
- Application logs
- Build logs
- System logs

### 2. Check Application Status

```powershell
# Via Cloudflare Tunnel
curl https://backend-openbo.devmosel.com/api/health

# Check headers
curl -I https://backend-openbo.devmosel.com/api/health
```

### 3. Database Logs (if managed by Coolify)

```
Database Service → Logs
```

## 🔥 Troubleshooting

### Error 502 Bad Gateway

**Cause:** Cloudflare Tunnel tidak bisa connect ke backend.

**Solutions:**

1. **Cek Port Configuration:**
   ```powershell
   # Di server, cek apakah Flask running di port 5000
   netstat -ano | findstr :5000
   ```

2. **Update Cloudflare Tunnel:**
   - Service URL harus: `http://localhost:5000`
   - Bukan: `http://localhost:80`

3. **Cek Coolify Logs:**
   ```
   Service → Logs
   ```
   
   Look for:
   - Flask startup message: `Running on http://0.0.0.0:5000`
   - Database connection errors
   - Port binding errors

4. **Restart Services:**
   ```
   Coolify Dashboard → Service → Restart
   ```

### Error 500 Internal Server Error

**Cause:** Application error atau database connection issue.

**Solutions:**

1. **Cek Environment Variables:**
   - Coolify → Service → Environment
   - Pastikan `DATABASE_URL` atau `DB_*` variables benar

2. **Cek Database Connection:**
   ```bash
   # Via Coolify Console
   python -c "from src.database import engine; print(engine)"
   ```

3. **Run Migration:**
   ```bash
   python migrate.py
   ```

### Error 404 Not Found

**Cause:** Route tidak ada atau base path salah.

**Solutions:**

1. **Cek Routes:**
   - Semua routes dimulai dengan `/api/`
   - Example: `/api/spaces`, `/api/auth/login`

2. **Cek Coolify Base Path:**
   - Settings → Base Path: `/` (kosong atau root)

### CORS Errors

**Cause:** Frontend domain tidak ada di `CORS_ORIGINS`.

**Solutions:**

1. **Update Environment Variable:**
   ```env
   CORS_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
   ```

2. **Restart Service:**
   ```
   Coolify → Service → Restart
   ```

## 🔐 Security Checklist

- [ ] `SECRET_KEY` di-generate dengan random value
- [ ] `JWT_SECRET_KEY` di-generate dengan random value
- [ ] `DEBUG=False` untuk production
- [ ] `CORS_ORIGINS` hanya allow frontend domains
- [ ] Database password strong & secure
- [ ] Cloudflare Tunnel authenticated
- [ ] SSL/TLS enabled (automatic via Cloudflare)
- [ ] Environment variables tidak di-commit ke Git

## 🚀 Production Best Practices

### 1. Environment Variables

**NEVER commit secrets to Git!**

Store di Coolify Environment Variables:
- SECRET_KEY
- JWT_SECRET_KEY
- DB_PASSWORD
- DATABASE_URL

### 2. Database Backup

Setup automatic backup di Coolify:
```
Database Service → Backups → Schedule
```

Atau manual:
```bash
# Via Coolify Console
mysqldump -u openbo -p openbo_db > backup_$(date +%Y%m%d).sql
```

### 3. Monitoring & Alerts

Setup di Coolify:
- Health check alerts
- Resource usage alerts
- Deployment notifications

### 4. Logging

Logs location di Coolify:
```
Service → Logs → Download
```

### 5. Resource Limits

Adjust di `.coolify.yml`:
```yaml
resources:
  limits:
    cpus: '2'        # Increase for production
    memory: 2G       # Increase for production
  reservations:
    cpus: '1'
    memory: 1G
```

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Code tested locally
- [ ] Database schema up to date (migrations)
- [ ] Environment variables configured
- [ ] Secret keys generated
- [ ] CORS origins configured
- [ ] Git repository connected to Coolify

### Deployment
- [ ] Code pushed to main branch
- [ ] Coolify auto-deploy triggered (or manual deploy)
- [ ] Build successful
- [ ] Container started
- [ ] Health check passing

### Post-Deployment
- [ ] Test `/api/health` endpoint
- [ ] Test authentication `/api/auth/login`
- [ ] Test main API endpoints
- [ ] Check logs for errors
- [ ] Verify database connection
- [ ] Test via frontend application
- [ ] Setup monitoring & alerts

## 🆘 Support & Resources

- **Coolify Docs:** https://coolify.io/docs
- **Cloudflare Tunnel:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- **Flask Docs:** https://flask.palletsprojects.com/

## Quick Commands Reference

```powershell
# Test health endpoint
curl https://backend-openbo.devmosel.com/api/health

# Test with headers
curl -I https://backend-openbo.devmosel.com/api/health

# Test API endpoint
curl https://backend-openbo.devmosel.com/api/spaces

# Check Cloudflare Tunnel status
cloudflared tunnel info <tunnel-name>

# Restart Cloudflare Tunnel (Windows)
Restart-Service cloudflared

# Restart Cloudflare Tunnel (Linux)
sudo systemctl restart cloudflared
```

---

**Setup Status:** Ready for Production  
**Domain:** backend-openbo.devmosel.com  
**Platform:** Coolify + Cloudflare Tunnel  
**Last Updated:** 2025-11-03
