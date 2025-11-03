# Pre-Deployment Checklist - OpenBO Backend

## ✅ Code Readiness

- [ ] All features tested locally
- [ ] No debug code or print statements in production code
- [ ] Error handling implemented
- [ ] API documentation complete (README.md)
- [ ] Git repository up to date
- [ ] `.gitignore` properly configured (no `.env` files committed)

## ✅ Configuration Files

- [ ] `Dockerfile` ready
- [ ] `Dockerfile.production` available for optimized build
- [ ] `docker-compose.yml` configured
- [ ] `.dockerignore` includes unnecessary files
- [ ] `.env.example` documented with all required variables
- [ ] `.coolify.yml` created (optional)

## ✅ Environment Variables

Prepare these values before deployment:

- [ ] `SECRET_KEY` - Generate random 32+ character string
- [ ] `JWT_SECRET_KEY` - Generate random key
- [ ] `DB_HOST` - Database host (from Coolify managed DB or external)
- [ ] `DB_PORT` - Usually 3306
- [ ] `DB_NAME` - Database name (e.g., openbo_db)
- [ ] `DB_USER` - Database user
- [ ] `DB_PASSWORD` - Strong database password
- [ ] `DATABASE_URL` - Full connection string
- [ ] `FLASK_ENV` - Set to "production"
- [ ] `DEBUG` - Set to "False"
- [ ] `CORS_ORIGINS` - Frontend domain(s)

### Generate Secret Keys

Run this to generate secure keys:

```python
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
```

## ✅ Database Setup

- [ ] Database server available (Coolify managed or external)
- [ ] Database created (`openbo_db`)
- [ ] Database user created with proper permissions
- [ ] Database accessible from Coolify server
- [ ] Firewall configured (if external DB)
- [ ] Backup strategy planned

## ✅ Coolify Configuration

- [ ] Coolify server running and accessible
- [ ] Project created in Coolify
- [ ] Git repository connected (or docker-compose ready)
- [ ] Branch selected (main/master)
- [ ] Build pack set to Dockerfile
- [ ] Port 5000 configured
- [ ] Environment variables added in Coolify UI
- [ ] Health check endpoint configured (`/api/health`)
- [ ] Resource limits set (CPU, Memory)

## ✅ Domain & SSL (Optional but Recommended)

- [ ] Domain purchased
- [ ] DNS A record pointing to Coolify server IP
- [ ] Domain added in Coolify service settings
- [ ] SSL certificate auto-provisioned (Let's Encrypt)
- [ ] Force HTTPS enabled
- [ ] CORS updated with actual domain

## ✅ Security

- [ ] No hardcoded secrets in code
- [ ] Strong passwords used
- [ ] CORS restricted to frontend domain only
- [ ] Database user has minimum required privileges
- [ ] `.env` file NOT committed to Git
- [ ] Debug mode disabled in production
- [ ] SQL injection protection (using ORM)
- [ ] Password hashing enabled (bcrypt)
- [ ] JWT tokens properly secured

## ✅ First Deployment

1. [ ] Deploy application via Coolify
2. [ ] Monitor deployment logs for errors
3. [ ] Deployment succeeds
4. [ ] Open Coolify shell/terminal for container
5. [ ] Run migrations:
   ```bash
   python migrate.py
   ```
6. [ ] Run seeding:
   ```bash
   python seed.py
   ```
7. [ ] Exit shell

## ✅ Post-Deployment Testing

- [ ] Access health endpoint: `https://your-domain.com/api/health`
  - Expected: `{"status": "healthy", ...}`
- [ ] Test login endpoint: `POST /api/auth/login`
  - Use seeded user credentials
  - Expected: Returns JWT token
- [ ] Test protected endpoint: `GET /api/spaces`
  - Include Authorization header
  - Expected: Returns space list
- [ ] Test CORS from frontend
- [ ] Verify database connections working
- [ ] Check logs for errors
- [ ] Test all critical endpoints

## ✅ Monitoring & Maintenance

- [ ] Coolify monitoring enabled
- [ ] Logs accessible via Coolify dashboard
- [ ] Alerts configured (optional)
- [ ] Backup schedule created
- [ ] Auto-deploy configured (optional)
- [ ] Documentation updated with production URLs

## ✅ Rollback Plan

- [ ] Previous version tagged in Git
- [ ] Database backup before migrations
- [ ] Know how to rollback:
  1. Coolify → Service → Deployments → Previous deployment
  2. Or redeploy specific Git commit
  3. Restore database from backup if needed

## Environment Variables Template

Copy this and fill in your values:

```bash
# Database
DB_HOST=your-db-host
DB_PORT=3306
DB_NAME=openbo_db
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
DATABASE_URL=mysql+pymysql://user:password@host:3306/openbo_db

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=False

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=86400

# CORS (comma-separated for multiple origins)
CORS_ORIGINS=https://your-frontend-domain.com

# Optional
PORT=5000
LOG_LEVEL=INFO
```

## Common Issues & Solutions

### Issue: Database connection failed
**Solution:** 
- Verify DATABASE_URL is correct
- Check DB host is accessible
- Ensure DB user has permissions

### Issue: Import errors
**Solution:**
- Ensure all dependencies in requirements.txt
- Rebuild Docker image
- Check Python version compatibility

### Issue: CORS errors
**Solution:**
- Update CORS_ORIGINS with exact frontend URL
- Include http/https protocol
- No trailing slash

### Issue: 502 Bad Gateway
**Solution:**
- Check application is running (Coolify logs)
- Verify port 5000 is exposed
- Check health endpoint working

## 🚀 Ready to Deploy?

If all checkboxes are ticked, you're ready to deploy!

1. Push code to Git repository
2. Open Coolify dashboard
3. Create new service
4. Configure environment variables
5. Deploy!
6. Monitor logs
7. Run migrations
8. Test endpoints
9. Celebrate! 🎉

---

**Need Help?**
- Coolify Docs: https://coolify.io/docs
- Flask Docs: https://flask.palletsprojects.com/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/
