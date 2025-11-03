# Coolify Deployment Guide - OpenBO Backend

## Prerequisites

- Coolify server sudah setup
- Database MariaDB/MySQL tersedia (bisa dari Coolify managed database atau external)
- Domain/subdomain untuk API (optional, bisa pakai IP)

## Deployment Steps di Coolify

### 1. Create New Resource

1. Login ke Coolify dashboard
2. Pilih project atau buat project baru
3. Click **"Add New Resource"**
4. Pilih **"Docker Compose"** atau **"Dockerfile"**

### 2. Setup Repository

**Option A: From Git Repository**
1. Connect repository (GitHub/GitLab/Bitbucket)
2. Pilih branch: `main`
3. Build Pack: **Dockerfile**

**Option B: From Docker Compose**
1. Paste `docker-compose.yml` content
2. Coolify akan detect services

### 3. Environment Variables (PENTING!)

Tambahkan environment variables berikut di Coolify:

```bash
# Database Configuration
DB_HOST=your-mariadb-host
DB_PORT=3306
DB_NAME=openbo_db
DB_USER=your-db-user
DB_PASSWORD=your-secure-password

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-min-32-characters-change-this
DEBUG=False

# Database URL (sesuaikan dengan DB credentials)
DATABASE_URL=mysql+pymysql://user:password@host:3306/openbo_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=86400

# CORS (atur sesuai frontend domain)
CORS_ORIGINS=https://your-frontend-domain.com,https://api.yourdomain.com
```

### 4. Port Configuration

- **Application Port**: `5000`
- Coolify akan auto-map ke public port atau domain

### 5. Health Check

Coolify akan check: `http://localhost:5000/api/health`

### 6. Database Setup

**Option A: Menggunakan Coolify Managed Database**
1. Add New Resource → Database → MariaDB
2. Catat credentials yang di-generate
3. Update environment variables backend dengan credentials tersebut

**Option B: External Database**
1. Ensure database accessible dari Coolify server
2. Configure firewall/security group untuk allow connection
3. Update environment variables

### 7. Pre-Deploy Commands (Migration & Seeding)

Di Coolify, pada **"Pre Deploy Command"** atau **"Build Command"**:

```bash
# Don't run migrate/seed automatically in production
# Run manually first time via shell
```

**Manual First Time Setup:**
1. Deploy application
2. Open **Shell/Terminal** di Coolify container
3. Run:
   ```bash
   python migrate.py
   python seed.py
   ```

### 8. Deploy!

1. Review configuration
2. Click **"Deploy"**
3. Monitor logs untuk errors
4. Test endpoints setelah deploy sukses

## Post-Deployment Checklist

- [ ] Test `/api/health` endpoint
- [ ] Test `/api/auth/login` dengan seeded user
- [ ] Test database connection
- [ ] Verify CORS working dengan frontend
- [ ] Check logs untuk errors
- [ ] Setup domain (optional)
- [ ] Setup SSL (Coolify auto-provisions Let's Encrypt)

## Coolify-Specific Configuration

### Custom Dockerfile untuk Production

Jika Dockerfile current kurang optimal, bisa gunakan multi-stage build:

```dockerfile
# Build stage
FROM python:3.13-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "run.py"]
```

### Docker Compose untuk Coolify (Simplified)

Jika menggunakan external database, gunakan compose simplified:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      FLASK_ENV: production
    restart: unless-stopped
```

Environment variables diatur via Coolify UI.

## Monitoring & Logs

### View Logs
- Coolify Dashboard → Your Service → Logs
- Real-time logs available

### Restart Service
- Coolify Dashboard → Your Service → Restart

### Shell Access
- Coolify Dashboard → Your Service → Terminal/Shell
- Useful untuk running migrations atau debugging

## Domain & SSL

1. **Add Domain** di Coolify service settings
2. **DNS Setup**: Point domain ke Coolify server IP
   ```
   A record: api.yourdomain.com → your.coolify.server.ip
   ```
3. **SSL**: Coolify auto-provisions Let's Encrypt
4. **Force HTTPS**: Enable di Coolify settings

## Troubleshooting

### Database Connection Failed

**Check:**
1. Environment variables benar
2. Database host accessible (test via telnet/nc)
3. Database credentials valid
4. Database exist dan migrations ran

**Fix:**
```bash
# Access shell
# Check connection manually
python -c "from src.config.database import db; from src.app import create_app; app = create_app(); app.app_context().push(); print(db.engine.url)"
```

### Port Already in Use

Coolify akan handle port mapping. Ensure `EXPOSE 5000` di Dockerfile.

### Module Import Errors

```bash
# Rebuild image
# Clear cache di Coolify
# Check requirements.txt complete
```

### CORS Errors

Update `CORS_ORIGINS` environment variable dengan actual frontend domain:
```
CORS_ORIGINS=https://app.yourdomain.com
```

## Security Best Practices

1. **Never commit `.env` file** - Use Coolify environment variables
2. **Use strong SECRET_KEY** - Generate via:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```
3. **Restrict CORS** - Only allow your frontend domain
4. **Database user** - Create user dengan least privileges
5. **Enable SSL** - Always use HTTPS in production
6. **Firewall** - Restrict database access to Coolify server IP only

## Scaling

Coolify supports:
- Horizontal scaling (multiple replicas)
- Resource limits (CPU, Memory)
- Load balancing

Configure in service settings.

## Backup Strategy

### Database Backup
1. Use Coolify backup feature (if managed DB)
2. Or setup cron job:
   ```bash
   mysqldump -h host -u user -ppass openbo_db > backup.sql
   ```

### Application Backup
- Code in Git (already backed up)
- Environment variables documented
- Database dumps scheduled

## CI/CD Integration

Coolify supports auto-deploy on git push:

1. Enable **Auto Deploy** di service settings
2. Select branch to watch
3. Push to branch → Auto deploy

## Resource Requirements

**Minimum:**
- CPU: 0.5 core
- RAM: 512 MB
- Disk: 1 GB

**Recommended:**
- CPU: 1 core
- RAM: 1 GB
- Disk: 5 GB

Configure in Coolify service settings.

---

## Quick Deploy Checklist

- [ ] Repository connected atau docker-compose ready
- [ ] Environment variables configured
- [ ] Database setup (managed atau external)
- [ ] Port 5000 exposed
- [ ] Dockerfile optimized
- [ ] Health check endpoint working
- [ ] CORS configured
- [ ] Secret keys generated
- [ ] First deployment tested
- [ ] Migrations ran manually
- [ ] Domain configured (optional)
- [ ] SSL enabled

**Ready to deploy!** 🚀

Need help? Check Coolify docs: https://coolify.io/docs
