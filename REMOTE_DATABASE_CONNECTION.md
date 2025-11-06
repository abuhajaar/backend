# Remote Database Connection Guide

## 📡 Connect dari PC Lokal ke Database Server

### Scenario
- **Database Server:** Server Coolify Anda (remote server)
- **Client:** PC lokal Anda (Windows)
- **Tool:** DBeaver

## 🔧 Metode 1: Direct Connection (Recommended untuk Development)

### **Prerequisites:**
1. Database port 3306 harus di-expose oleh server
2. Firewall server harus allow port 3306
3. Database user harus allow remote connections

### **DBeaver Connection Settings:**

```
Connection Type: MariaDB
Server Host: <IP-SERVER-ANDA>  # Contoh: 192.168.1.100
Port: 3306
Database: openbo_db
Username: openbo_user
Password: openbo_pass
```

**Example:**
```
┌─────────────────────────────────────┐
│ Connection Settings                  │
├─────────────────────────────────────┤
│ Host:     203.0.113.100  (IP server)│
│ Port:     3306                       │
│ Database: openbo_db                  │
│ Username: openbo_user                │
│ Password: ********                   │
└─────────────────────────────────────┘
```

### **Setup di Server:**

#### **1. Expose Database Port di Docker**

Jika menggunakan Docker Compose, pastikan port di-expose:

```yaml
# docker-compose.yaml
services:
  db:
    image: mariadb:11.2
    ports:
      - "3306:3306"  # ✅ Port exposed to host
    # atau bind ke IP spesifik:
    # - "0.0.0.0:3306:3306"
```

#### **2. Allow Remote Connections di MariaDB**

Connect ke database server dan run:

```sql
-- Allow user from any host (% = wildcard)
CREATE USER 'openbo_user'@'%' IDENTIFIED BY 'openbo_pass';
GRANT ALL PRIVILEGES ON openbo_db.* TO 'openbo_user'@'%';
FLUSH PRIVILEGES;

-- Atau allow dari IP spesifik PC Anda
CREATE USER 'openbo_user'@'192.168.1.50' IDENTIFIED BY 'openbo_pass';
GRANT ALL PRIVILEGES ON openbo_db.* TO 'openbo_user'@'192.168.1.50';
FLUSH PRIVILEGES;
```

#### **3. Configure MariaDB untuk Accept Remote Connections**

Edit MariaDB config (jika perlu):

```bash
# Connect ke container
docker exec -it openbo_db bash

# Edit config (jika ada)
# File biasanya di /etc/mysql/mariadb.conf.d/50-server.cnf
# Pastikan bind-address = 0.0.0.0 (bukan 127.0.0.1)
```

Atau tambahkan di `docker-compose.yaml`:

```yaml
services:
  db:
    command: --bind-address=0.0.0.0
```

#### **4. Open Firewall Port di Server**

**Windows Server:**
```powershell
# Allow port 3306 inbound
New-NetFirewallRule -DisplayName "MariaDB" -Direction Inbound -LocalPort 3306 -Protocol TCP -Action Allow
```

**Linux Server:**
```bash
# UFW
sudo ufw allow 3306/tcp

# Or Firewalld
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

**Coolify:**
Jika menggunakan Coolify, check firewall settings di dashboard.

## 🔐 Metode 2: SSH Tunnel (RECOMMENDED untuk Production - Lebih Aman!)

Gunakan SSH tunnel untuk enkripsi koneksi. Tidak perlu expose port 3306 ke public.

### **Setup SSH Tunnel:**

#### **Option A: Manual SSH Tunnel via PowerShell**

```powershell
# Buka SSH tunnel
ssh -L 3307:localhost:3306 user@<SERVER-IP>

# Keep terminal open!
# Port local 3307 akan forward ke port 3306 di server
```

#### **Option B: DBeaver Built-in SSH Tunnel**

1. **Buka DBeaver → New Connection → MariaDB**

2. **Tab "Main":**
   ```
   Host: localhost
   Port: 3306
   Database: openbo_db
   Username: openbo_user
   Password: openbo_pass
   ```

3. **Tab "SSH":**
   - ☑ **Use SSH Tunnel**
   ```
   Host/IP: <IP-SERVER-ANDA>
   Port: 22
   User Name: <SSH-USERNAME>
   Authentication Method: Password (atau Public Key)
   Password: <SSH-PASSWORD>
   ```

4. **Test Connection** → Should work! ✅

### **Diagram SSH Tunnel:**

```
┌─────────────┐    SSH Tunnel (Port 22)     ┌──────────────┐
│  PC Lokal   │ ──────────────────────────→ │    Server    │
│  DBeaver    │  Encrypted Connection       │              │
└─────────────┘                              │  ┌────────┐  │
                                             │  │MariaDB │  │
                                             │  │:3306   │  │
                                             │  └────────┘  │
                                             └──────────────┘
```

## 🌐 Metode 3: Cloudflare Tunnel (Jika sudah setup)

Jika Anda sudah punya Cloudflare Tunnel untuk backend, bisa tambah service untuk database:

```yaml
# Cloudflare Tunnel config
ingress:
  - hostname: backend-openbo.devmosel.com
    service: http://localhost:5000
    
  - hostname: db-openbo.devmosel.com  # ← Database endpoint
    service: tcp://localhost:3306
    
  - service: http_status:404
```

**DBeaver Connection:**
```
Host: db-openbo.devmosel.com
Port: 3306
Database: openbo_db
Username: openbo_user
Password: openbo_pass
```

## 🧪 Testing Connection

### **1. Test Port Accessibility dari PC**

```powershell
# Test if server port 3306 is reachable
Test-NetConnection -ComputerName <SERVER-IP> -Port 3306

# Expected output:
# TcpTestSucceeded : True
```

### **2. Test dengan MySQL Client**

```powershell
# Install MySQL client if not installed
# Then connect:
mysql -h <SERVER-IP> -P 3306 -u openbo_user -p openbo_db

# Enter password: openbo_pass
```

### **3. Test di DBeaver**

Click **"Test Connection"** button → Should see **"Connected"** ✅

## 🔒 Security Best Practices

### **❌ TIDAK AMAN (Jangan untuk Production!):**
- Expose port 3306 ke public internet
- Allow connections from any host (%)
- Gunakan weak password

### **✅ AMAN (Recommended untuk Production):**
1. **Use SSH Tunnel** untuk koneksi remote
2. **Whitelist IP specific** di firewall
3. **Strong password** untuk database user
4. **Separate read-only user** untuk query
5. **VPN connection** jika memungkinkan

### **Setup Read-Only User (Recommended):**

```sql
-- Create read-only user for remote access
CREATE USER 'openbo_readonly'@'%' IDENTIFIED BY 'strong-password-here';
GRANT SELECT ON openbo_db.* TO 'openbo_readonly'@'%';
FLUSH PRIVILEGES;
```

Connect dengan user ini untuk read-only access.

## 📊 Connection Options Comparison

| Method | Security | Speed | Setup Complexity | Production Ready |
|--------|----------|-------|------------------|------------------|
| Direct Connection | ⚠️ Low | ⚡ Fast | 🟢 Easy | ❌ No |
| SSH Tunnel | ✅ High | ⚡ Fast | 🟡 Medium | ✅ Yes |
| Cloudflare Tunnel | ✅ High | 🟡 Medium | 🔴 Complex | ✅ Yes |
| VPN | ✅ Highest | ⚡ Fast | 🔴 Complex | ✅ Yes |

## 🚀 Quick Start Guide

### **For Development (Simple):**

1. **Di Server:**
   ```powershell
   # Pastikan port 3306 exposed di docker-compose.yaml
   docker-compose restart db
   ```

2. **Di PC Lokal (DBeaver):**
   ```
   Host: <IP-SERVER>
   Port: 3306
   Database: openbo_db
   User: openbo_user
   Pass: openbo_pass
   ```

3. **Test Connection** → Done! ✅

### **For Production (Secure):**

1. **Setup SSH Tunnel di DBeaver:**
   - Main tab: `localhost:3306`
   - SSH tab: Enable + masukkan server SSH credentials
   
2. **Test Connection** → Done! ✅

## 🔍 Troubleshooting

### **Error: "Connection Refused"**

**Cause:** Port tidak exposed atau firewall block.

**Fix:**
```powershell
# Di server, check port listening
netstat -ano | findstr :3306

# Check firewall
Test-NetConnection -ComputerName <SERVER-IP> -Port 3306
```

### **Error: "Access Denied for user"**

**Cause:** User tidak punya permission untuk remote access.

**Fix:**
```sql
-- Di server database
GRANT ALL PRIVILEGES ON openbo_db.* TO 'openbo_user'@'%';
FLUSH PRIVILEGES;
```

### **Error: "Unknown Database"**

**Cause:** Database name salah atau belum dibuat.

**Fix:**
```sql
-- Check databases
SHOW DATABASES;

-- Create if missing
CREATE DATABASE openbo_db;
```

### **Connection Timeout**

**Cause:** Firewall atau network issue.

**Fix:**
1. Check server firewall allows port 3306
2. Check cloud provider security groups
3. Try SSH tunnel instead

## 📝 Example Configurations

### **Docker Compose - Expose Database:**

```yaml
services:
  db:
    image: mariadb:11.2
    ports:
      - "3306:3306"  # Expose to all interfaces
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: openbo_db
      MYSQL_USER: openbo_user
      MYSQL_PASSWORD: openbo_pass
    command: --bind-address=0.0.0.0  # Allow remote connections
```

### **DBeaver SSH Connection Profile:**

```
[Connection: OpenBO Production DB]
Main:
  Host: localhost
  Port: 3306
  Database: openbo_db
  Username: openbo_user
  Password: openbo_pass

SSH:
  ☑ Use SSH Tunnel
  Host: your-server-ip
  Port: 22
  User: your-ssh-username
  Auth: Public Key (or Password)
  Key: C:\Users\YourUser\.ssh\id_rsa
```

## 🎯 Recommended Setup

**Untuk Development:**
- ✅ Direct connection via IP
- ✅ Whitelist your PC IP di firewall
- ✅ Use strong password

**Untuk Production:**
- ✅ SSH Tunnel (DBeaver built-in)
- ✅ VPN connection jika ada
- ✅ Read-only user untuk query
- ❌ Jangan expose port 3306 ke public

---

**Need Help?**

Check these:
1. Server IP: `ipconfig` atau `ip addr`
2. Port status: `netstat -ano | findstr :3306`
3. Firewall: `Test-NetConnection -Port 3306`
4. User permissions: `SHOW GRANTS FOR 'openbo_user'@'%';`
