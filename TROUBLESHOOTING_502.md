# Troubleshooting 502 Error - Cloudflare Tunnel

## ✅ MASALAH TERSELESAIKAN

### Root Cause
Flask application hanya listening pada `localhost` (127.0.0.1), sehingga tidak bisa diakses dari Cloudflare Tunnel yang mencoba connect dari external network.

### Solusi yang Diterapkan
Changed `run.py` dari:
```python
host='localhost'  # ❌ Hanya accept loopback connections
```

Menjadi:
```python
host='0.0.0.0'    # ✅ Accept connections dari semua network interfaces
```

## Cara Verify Fix

### 1. Cek Container Status
```powershell
docker-compose ps
```

**Expected Output:**
```
NAME                    STATUS
backend-backend-1       Up
backend-db-1           Up (healthy)
```

### 2. Cek Backend Logs
```powershell
docker-compose logs backend
```

**Expected Output:**
```
* Running on http://0.0.0.0:5000
* Running on http://192.168.1.103:5000  # Container IP
```

### 3. Test dari Local Network
```powershell
curl http://192.168.1.103:5000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### 4. Test via Cloudflare Tunnel
```
curl https://your-tunnel-domain.com/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

## Cloudflare Tunnel Configuration

### Correct Configuration
Pastikan Cloudflare Tunnel config mengarah ke:

**Option A - Docker Container IP:**
```yaml
ingress:
  - service: http://backend:5000  # Service name dari docker-compose
```

**Option B - Localhost (dari host machine):**
```yaml
ingress:
  - service: http://localhost:5000
```

## Troubleshooting Lainnya

### Error 502 Masih Terjadi?

#### 1. **Cek Container Running**
```powershell
docker-compose ps
```

Jika status `Exit`:
```powershell
docker-compose logs backend
```

#### 2. **Cek Port Binding**
```powershell
docker-compose ps
```

Pastikan `0.0.0.0:5000->5000/tcp` muncul di kolom PORTS.

#### 3. **Cek Database Connection**
```powershell
docker-compose logs backend | Select-String -Pattern "DATABASE_URL"
```

Pastikan `DB_HOST=db` (bukan `localhost`).

#### 4. **Cek Firewall**
```powershell
# Test port 5000 accessible
Test-NetConnection -ComputerName localhost -Port 5000
```

#### 5. **Rebuild Container (jika ada perubahan code)**
```powershell
docker-compose down
docker-compose up --build -d
```

## Common Issues

### Issue: Container exits immediately
**Diagnosis:**
```powershell
docker-compose logs backend
```

**Solutions:**
- Database connection error → Cek `DB_HOST=db` di `.env`
- Migration error → Cek `docker-compose logs db`
- Python error → Cek syntax errors di code

### Issue: Database connection refused
**Diagnosis:**
```powershell
docker-compose logs db
```

**Solutions:**
```powershell
# Restart database
docker-compose restart db

# Wait for database ready
docker-compose exec db mysql -u openbo -p -e "SELECT 1"
```

### Issue: CORS errors
**Diagnosis:**
Browser console shows CORS error.

**Solutions:**
Update `.env`:
```env
CORS_ORIGINS=https://your-frontend-domain.com
```

Restart backend:
```powershell
docker-compose restart backend
```

## Health Check Commands

### 1. Check All Services
```powershell
docker-compose ps
```

### 2. Check Backend Health
```powershell
docker-compose exec backend python -c "from src.app import create_app; app = create_app(); print('App OK')"
```

### 3. Check Database Health
```powershell
docker-compose exec db mysqladmin ping -h localhost -u openbo -p
```

### 4. Check Network Connectivity
```powershell
# From backend container to database
docker-compose exec backend ping db -c 3

# From host to backend
curl http://localhost:5000/api/health
```

## Production Checklist

- [x] `host='0.0.0.0'` in `run.py`
- [x] `DB_HOST=db` in `.env`
- [x] Port 5000 exposed in `docker-compose.yaml`
- [x] Environment variables set correctly
- [ ] CORS_ORIGINS configured for frontend domain
- [ ] SECRET_KEY changed from default
- [ ] JWT_SECRET_KEY changed from default
- [ ] SSL/HTTPS enabled on Cloudflare Tunnel
- [ ] Database backup strategy in place
- [ ] Monitoring setup (logs, health checks)

## Next Steps

1. **Update Environment Variables:**
   - Generate new SECRET_KEY & JWT_SECRET_KEY
   - Set CORS_ORIGINS to frontend domain
   - Set DEBUG=False for production

2. **Setup Monitoring:**
   ```powershell
   # Watch logs in real-time
   docker-compose logs -f backend
   ```

3. **Setup Backup:**
   ```powershell
   # Backup database
   docker-compose exec db mysqldump -u openbo -p openbo_db > backup.sql
   ```

4. **Configure Cloudflare:**
   - Enable SSL/TLS (Full mode)
   - Setup firewall rules
   - Configure rate limiting
   - Enable DDoS protection

## Support

Jika masih ada issue:
1. Check logs: `docker-compose logs backend`
2. Check database: `docker-compose logs db`
3. Check network: `docker network inspect backend_openbo_network`
4. Test endpoints: `curl -v http://localhost:5000/api/health`

---

**Status:** ✅ RESOLVED  
**Fix Applied:** 2025-11-03  
**Backend Version:** Flask 3.0.0  
**Deployment Method:** Docker Compose + Cloudflare Tunnel
