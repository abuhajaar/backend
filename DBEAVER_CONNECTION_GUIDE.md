# DBeaver Connection Guide - MariaDB Docker Container

## 📋 Informasi Database

Berdasarkan `docker-compose.yaml`:

```
Container Name: openbo_db
Database Type: MariaDB 11.2
Port Mapping: 3306:3306 (Host:Container)
Database Name: openbo_db
Username: openbo_user
Password: openbo_pass
Root Password: rootpassword
```

## 🔧 Cara Connect DBeaver

### **Metode 1: Connect via Localhost (RECOMMENDED)**

Karena port 3306 sudah di-expose ke host, Anda bisa connect langsung.

#### **Step-by-step:**

1. **Buka DBeaver**
   - File → New → Database Connection
   - Atau klik icon **"New Database Connection"** (plug icon)

2. **Pilih Database Type**
   - Select: **MariaDB**
   - Click **Next**

3. **Connection Settings - Main Tab:**
   ```
   Server Host: localhost
   Port: 3306
   Database: openbo_db
   Username: openbo_user
   Password: openbo_pass
   ```

4. **Connection Settings - Advanced Options:**
   - Driver properties → Add:
     - `allowPublicKeyRetrieval`: `true`
     - `useSSL`: `false`

5. **Test Connection:**
   - Click **"Test Connection"**
   - Jika belum install driver, klik **"Download"** untuk download MariaDB driver
   - Seharusnya muncul: **"Connected"** ✅

6. **Save & Connect:**
   - Click **Finish**
   - Database akan muncul di Database Navigator

### **Metode 2: Connect via IP Address**

Jika localhost tidak work, gunakan IP address:

```
Server Host: 127.0.0.1
Port: 3306
Database: openbo_db
Username: openbo_user
Password: openbo_pass
```

### **Metode 3: Connect sebagai Root User**

Untuk full access:

```
Server Host: localhost
Port: 3306
Database: openbo_db
Username: root
Password: rootpassword
```

## 🐳 Verifikasi Container Running

Sebelum connect, pastikan container running:

```powershell
# Cek status container
docker-compose ps

# Expected output:
# NAME            STATUS
# openbo_db       Up (healthy)
# openbo_backend  Up
```

Jika container tidak running:
```powershell
# Start containers
docker-compose up -d

# Check logs jika ada error
docker-compose logs db
```

## 🧪 Test Connection dari Terminal

Sebelum menggunakan DBeaver, test dulu dari terminal:

### **Windows PowerShell:**

```powershell
# Test port 3306 accessible
Test-NetConnection -ComputerName localhost -Port 3306

# Expected output:
# TcpTestSucceeded : True
```

### **Test dengan MySQL Client (jika installed):**

```powershell
# Connect to database
mysql -h localhost -P 3306 -u openbo_user -p openbo_db

# Password: openbo_pass
```

### **Test via Docker exec:**

```powershell
# Connect to database container
docker exec -it openbo_db mysql -u openbo_user -p openbo_db

# Password: openbo_pass
```

Setelah connect, test query:
```sql
SHOW TABLES;
SELECT * FROM users LIMIT 5;
```

## 🔥 Troubleshooting

### **Error: "Connection Refused" atau "Can't Connect"**

**Cause:** Container tidak running atau port tidak di-expose.

**Solutions:**

1. **Check container status:**
   ```powershell
   docker-compose ps
   ```

2. **Check if port 3306 is listening:**
   ```powershell
   netstat -ano | findstr :3306
   ```

3. **Restart containers:**
   ```powershell
   docker-compose restart db
   ```

4. **Check logs:**
   ```powershell
   docker-compose logs db
   ```

### **Error: "Access Denied"**

**Cause:** Username atau password salah.

**Solutions:**

1. **Verify credentials di docker-compose.yaml:**
   ```yaml
   MYSQL_USER: openbo_user
   MYSQL_PASSWORD: openbo_pass
   ```

2. **Reset password (jika lupa):**
   ```powershell
   # Stop containers
   docker-compose down
   
   # Remove database volume
   docker volume rm backend_mariadb_data
   
   # Start again (will recreate database)
   docker-compose up -d
   ```

### **Error: "Unknown Database"**

**Cause:** Database belum dibuat atau nama salah.

**Solutions:**

1. **Check database exists:**
   ```powershell
   docker exec -it openbo_db mysql -u root -p -e "SHOW DATABASES;"
   # Password: rootpassword
   ```

2. **Create database if missing:**
   ```powershell
   docker exec -it openbo_db mysql -u root -p -e "CREATE DATABASE openbo_db;"
   # Password: rootpassword
   ```

### **Error: "Driver Not Found" di DBeaver**

**Cause:** MariaDB JDBC driver belum terinstall.

**Solutions:**

1. DBeaver akan auto-prompt untuk download driver
2. Atau manual: Database → Driver Manager → MariaDB → Download

### **Port 3306 Already in Use**

**Cause:** Ada service lain (MySQL/MariaDB) running di port 3306.

**Solutions:**

**Option A - Stop service yang conflict:**
```powershell
# Check what's using port 3306
netstat -ano | findstr :3306

# Stop MySQL service (jika ada)
Stop-Service MySQL
# atau
Stop-Service MariaDB
```

**Option B - Change Docker port mapping:**

Edit `docker-compose.yaml`:
```yaml
ports:
  - "3307:3306"  # Use port 3307 instead
```

Then connect with:
```
Server Host: localhost
Port: 3307  # ← Changed port
```

## 📊 DBeaver Tips & Tricks

### **1. Save Password (Optional)**

Untuk tidak perlu input password setiap kali:
- Edit Connection → Main tab
- Check: **"Save password"**

### **2. Set Default Database**

- Edit Connection → Main tab
- Database: `openbo_db`

### **3. SQL Editor Shortcuts**

```
Ctrl + Enter     - Execute current query
Ctrl + Shift + E - Execute script
Ctrl + /         - Comment/uncomment line
Ctrl + Space     - Auto-complete
```

### **4. View Database Structure**

```
Database Navigator → openbo_db → Tables
Right-click table → View Data
Right-click table → Generate SQL → SELECT
```

### **5. Export/Import Data**

**Export:**
- Right-click table → Export Data
- Choose format: CSV, JSON, SQL, Excel

**Import:**
- Right-click table → Import Data
- Choose source file

### **6. ER Diagram**

View database relationships:
- Right-click database → ER Diagram
- Will show tables and foreign keys

## 🔐 Security Best Practices

### **Production Environment:**

1. **Change default passwords:**
   ```yaml
   MYSQL_ROOT_PASSWORD: <strong-random-password>
   MYSQL_PASSWORD: <strong-random-password>
   ```

2. **Don't expose port publicly:**
   ```yaml
   ports:
     - "127.0.0.1:3306:3306"  # Only localhost access
   ```

3. **Use .env file for secrets:**
   ```yaml
   environment:
     MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
     MYSQL_PASSWORD: ${DB_PASSWORD}
   ```

4. **Limit user permissions:**
   ```sql
   GRANT SELECT, INSERT, UPDATE, DELETE ON openbo_db.* TO 'openbo_user'@'%';
   FLUSH PRIVILEGES;
   ```

## 📚 Useful SQL Queries

### **Check Database Info:**
```sql
-- Show all tables
SHOW TABLES;

-- Show table structure
DESCRIBE users;
SHOW CREATE TABLE users;

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM bookings;

-- Check database size
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'openbo_db'
GROUP BY table_schema;
```

### **Check Active Connections:**
```sql
SHOW PROCESSLIST;
```

### **Check User Privileges:**
```sql
SHOW GRANTS FOR 'openbo_user'@'%';
```

## 🎯 Quick Connection Summary

### **For Local Development (DBeaver):**
```
Host: localhost
Port: 3306
Database: openbo_db
User: openbo_user
Password: openbo_pass
```

### **For Application (Flask):**
```
DATABASE_URL: mysql+pymysql://openbo_user:openbo_pass@db:3306/openbo_db
(db hostname karena dalam Docker network)
```

### **For Root Access:**
```
Host: localhost
Port: 3306
Database: openbo_db
User: root
Password: rootpassword
```

---

**Last Updated:** 2025-11-03  
**Database Version:** MariaDB 11.2  
**Container:** openbo_db
