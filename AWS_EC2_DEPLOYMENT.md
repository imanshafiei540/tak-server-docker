# TAK Server AWS EC2 Deployment Guide

> **Complete guide for deploying TAK Server to Amazon Web Services EC2**

This guide walks you through deploying your TAK server from local development to production on AWS EC2, including security considerations, scaling, and maintenance.

## 📋 Table of Contents

1. [AWS EC2 Setup](#aws-ec2-setup)
2. [Security Configuration](#security-configuration)
3. [TAK Server Deployment](#tak-server-deployment)
4. [SSL Certificate Management](#ssl-certificate-management)
5. [Domain Setup](#domain-setup)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Backup Strategy](#backup-strategy)
8. [Troubleshooting](#troubleshooting)
9. [Cost Optimization](#cost-optimization)

## 🚀 AWS EC2 Setup

### Step 1: Launch EC2 Instance

#### **Recommended Configuration:**
- **AMI:** Ubuntu 22.04 LTS (HVM) - `ami-0c7217cdde317cfec` (us-east-1)
- **Instance Type:** `t3.large` (2 vCPU, 8GB RAM)
- **Storage:** 50GB GP3 SSD
- **Key Pair:** Create or use existing SSH key

```bash
# Using AWS CLI (optional)
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --count 1 \
    --instance-type t3.large \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":50,"VolumeType":"gp3"}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=TAK-Server}]'
```

### Step 2: Security Groups Configuration

Create a security group with the following rules:

```bash
# Create security group
aws ec2 create-security-group \
    --group-name tak-server-sg \
    --description "TAK Server Security Group"

# SSH Access (restrict to your IP)
aws ec2 authorize-security-group-ingress \
    --group-name tak-server-sg \
    --protocol tcp \
    --port 22 \
    --source-group YOUR.IP.ADDRESS.HERE/32

# TAK Server Ports
TAK_PORTS=(8089 8443 8444 8446 9000 9001)
for port in "${TAK_PORTS[@]}"; do
    aws ec2 authorize-security-group-ingress \
        --group-name tak-server-sg \
        --protocol tcp \
        --port $port \
        --cidr 0.0.0.0/0
done
```

#### **Required Ports:**
| Port | Protocol | Purpose | Restrict? |
|------|----------|---------|-----------|
| 22   | TCP      | SSH Access | ✅ Your IP only |
| 5432 | TCP      | PostgreSQL | 🔒 Internal only |
| 8089 | TCP      | TAK SSL Client | 🌐 Public |
| 8443 | TCP      | Web Interface | 🌐 Public |
| 8444 | TCP      | Certificate Auth | 🌐 Public |
| 8446 | TCP      | API Access | 🌐 Public |
| 9000 | TCP      | Streaming | 🌐 Public |
| 9001 | TCP      | Federation | 🌐 Public |

### Step 3: Elastic IP (Recommended)

```bash
# Allocate Elastic IP
aws ec2 allocate-address --domain vpc

# Associate with instance
aws ec2 associate-address \
    --instance-id i-1234567890abcdef0 \
    --public-ip YOUR.ELASTIC.IP
```

## 🔐 Security Configuration

### Step 1: Connect to Your Instance

```bash
# SSH to your EC2 instance
ssh -i your-key.pem ubuntu@YOUR.ELASTIC.IP

# Update system
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Prerequisites

```bash
# Install required packages
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    net-tools \
    unzip \
    zip \
    git

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test Docker
docker run hello-world
```

## 🚀 TAK Server Deployment

> **💡 IP vs Domain:** You can use either an IP address OR a domain name. IP addresses work perfectly for most deployments!

### Step 1: Clone and Prepare Repository

```bash
# Clone the repository
git clone https://github.com/Cloud-RF/tak-server.git
cd tak-server

# Upload your TAK release file (from local machine)
# scp -i your-key.pem takserver-docker-5.4-RELEASE-19.zip ubuntu@YOUR.ELASTIC.IP:~/tak-server/
```

### Step 2: Configure Environment

```bash
# Create environment file
cat << EOF > .env
# Server Configuration
COUNTRY=US
STATE=YOUR_STATE
CITY=YOUR_CITY
ORGANIZATIONAL_UNIT=TAK
ORGANIZATION=YOUR_ORG

# Set your EC2 public IP or domain
PUBLIC_IP=YOUR.ELASTIC.IP
EOF
```

### Step 3: Update Configuration Files

```bash
# Update CoreConfig.xml with your public IP
sed -i "s/HOSTIP/YOUR.ELASTIC.IP/g" CoreConfig.xml

# Or if using a domain name
sed -i "s/HOSTIP/your-domain.com/g" CoreConfig.xml
```

### Step 4: Run Setup

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run the setup
./scripts/setup.sh
```

**Expected Setup Time:** 5-10 minutes

### Step 5: Verify Deployment

```bash
# Check containers
docker ps

# Check logs
docker logs tak-server-tak-1

# Test connectivity
curl -k https://YOUR.ELASTIC.IP:8443

# Check if all ports are listening
netstat -tlnp | grep -E ":(8089|8443|8444|8446|9000|9001)"
```

**✅ Success! If setup completed, you'll see:**
```
Import the admin.p12 certificate from this folder to your browser's certificate store as per the README.md file
Login at https://YOUR.IP:8443 with your admin account. No need to run the /setup step as this has been done.
Certificates and .zip data packages are in tak/certs/files
```

**For IP-only deployment (no domain needed):**
- ✅ Your server is ready at: `https://10.212.2.206:8443` (replace with your IP)
- ✅ Download certificates from: `tak/certs/files/admin.p12`
- ✅ Client connection: `10.212.2.206:8089`
- ✅ **You're done!** Skip all domain configuration sections below

**Next steps for IP-only deployment:**
1. **Download certificate from EC2:**
   ```bash
   scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/admin.p12 ~/Downloads/
   ```
2. Import `admin.p12` to browser (password: `atakatak`)
3. Access: `https://10.212.2.206:8443`
4. Create users and download client certificates

## 🔒 SSL Certificate Management

### Option 1: Let's Encrypt (Recommended for Production)

```bash
# Install Certbot
sudo apt install -y certbot

# Get certificate (requires domain name)
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
```

### Option 2: Use Generated Certificates (Development)

The setup script generates self-signed certificates which work for testing but will show browser warnings.

### Option 3: Upload Your Own Certificates

```bash
# If you have existing certificates
sudo cp your-cert.pem /etc/ssl/certs/
sudo cp your-key.pem /etc/ssl/private/
sudo chmod 644 /etc/ssl/certs/your-cert.pem
sudo chmod 600 /etc/ssl/private/your-key.pem
```

## 🌐 Domain Setup

### Step 1: Configure DNS

Point your domain to your Elastic IP:

```
Type: A Record
Name: tak (or @ for root domain)
Value: YOUR.ELASTIC.IP
TTL: 300
```

### Step 2: Update TAK Configuration

```bash
# Update all configuration files with your domain
sed -i "s/YOUR\.ELASTIC\.IP/your-domain.com/g" CoreConfig.xml
sed -i "s/YOUR\.ELASTIC\.IP/your-domain.com/g" .env

# Restart containers
docker compose down
docker compose up -d
```

### Step 3: Verify Domain Access

```bash
# Test domain access
curl -k https://your-domain.com:8443
```

## 📊 Monitoring & Maintenance

### Setup Log Rotation

```bash
# Configure logrotate for TAK logs
sudo cat << EOF > /etc/logrotate.d/tak-server
/home/ubuntu/tak-server/tak/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### Monitor Resource Usage

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Monitor containers
docker stats

# Check TAK server logs
docker logs -f tak-server-tak-1
```

### Automated Health Checks

```bash
# Create health check script
cat << 'EOF' > ~/health-check.sh
#!/bin/bash
if curl -k -s https://localhost:8443 > /dev/null; then
    echo "$(date): TAK Server is healthy"
else
    echo "$(date): TAK Server is down! Restarting..."
    cd ~/tak-server && docker compose restart
fi
EOF

chmod +x ~/health-check.sh

# Add to crontab (check every 5 minutes)
echo "*/5 * * * * /home/ubuntu/health-check.sh >> /home/ubuntu/health-check.log 2>&1" | crontab -
```

## 💾 Backup Strategy

### Automated Backup Script

```bash
# Create backup script
cat << 'EOF' > ~/backup-tak.sh
#!/bin/bash

BACKUP_DIR="/home/ubuntu/tak-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="tak-backup-$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Stop containers
cd ~/tak-server
docker compose down

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    tak/ \
    .env \
    CoreConfig.xml \
    docker-compose.yml

# Restart containers
docker compose up -d

# Keep only last 7 days of backups
find $BACKUP_DIR -name "tak-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x ~/backup-tak.sh

# Schedule daily backups at 2 AM
echo "0 2 * * * /home/ubuntu/backup-tak.sh >> /home/ubuntu/backup.log 2>&1" | crontab -
```

### AWS EBS Snapshots

```bash
# Create snapshot of EBS volume
aws ec2 create-snapshot \
    --volume-id vol-xxxxxxxxx \
    --description "TAK Server Backup $(date)"

# Automate with lifecycle policy in AWS Console
```

## 🔧 Troubleshooting

### Common Issues

#### "Connection Refused"
```bash
# Check if containers are running
docker ps

# Check Security Groups allow the ports
aws ec2 describe-security-groups --group-names tak-server-sg

# Check UFW status
sudo ufw status
```

#### "SSL Certificate Errors"
```bash
# Regenerate certificates
docker exec -it tak-server-tak-1 bash -c "cd /opt/tak/certs && ./makeCert.sh client user1"

# Check certificate validity
openssl x509 -in tak/certs/files/user1.pem -text -noout
```

#### "High Memory Usage"
```bash
# Check container resource usage
docker stats

# Restart containers to free memory
docker compose restart

# Consider upgrading instance type
```

#### "Database Connection Issues"
```bash
# Check database container
docker logs tak-server-db-1

# Test database connection
docker exec -it tak-server-db-1 psql -U martiuser -d cot -c "\dt"
```

### Emergency Recovery

```bash
# Complete restart
cd ~/tak-server
docker compose down
docker system prune -f
docker compose up -d

# Restore from backup
cd ~/
tar -xzf tak-backups/tak-backup-YYYYMMDD_HHMMSS.tar.gz
cd tak-server
docker compose up -d
```

## 💰 Cost Optimization

### Reserved Instances
- Save 30-60% with 1-3 year commitments
- Best for production deployments

### Spot Instances
- Save up to 90% for non-critical testing
- Risk of termination when demand increases

### Auto-scaling (Advanced)
```bash
# For high-traffic deployments, consider:
# - Application Load Balancer
# - Auto Scaling Groups
# - RDS for managed PostgreSQL
```

### Cost Monitoring
```bash
# Set up AWS Cost Alerts
aws budgets create-budget \
    --account-id 123456789012 \
    --budget file://budget.json
```

## 🎯 Success Checklist

- [ ] EC2 instance launched with Ubuntu 22.04 LTS
- [ ] Security groups configured with required ports
- [ ] Elastic IP assigned and DNS configured
- [ ] Docker and dependencies installed
- [ ] TAK server deployed and running
- [ ] SSL certificates configured
- [ ] Domain name pointing to server (if applicable)
- [ ] Health monitoring script configured
- [ ] Backup strategy implemented
- [ ] Firewall rules configured
- [ ] Cost alerts configured

## 📱 Client Configuration

### ATAK/iTAK Configuration
1. Download client certificates from: `https://your-domain.com:8443`
2. Import certificates to device
3. Configure server connection:
   - Server: `your-domain.com`
   - Port: `8089`
   - Protocol: `SSL`

### Data Package Generation
```bash
# Generate client data packages
docker exec -it tak-server-tak-1 bash -c "cd /opt/tak/certs && ./makeCert.sh client newuser"

# Download data packages from
# https://your-domain.com:8443/Marti/api/tls/signClient/newuser
```

## 🔗 Useful Commands

```bash
# View all containers
docker ps -a

# Follow TAK server logs
docker logs -f tak-server-tak-1

# Access TAK server shell
docker exec -it tak-server-tak-1 bash

# Restart specific service
docker compose restart tak

# Update and restart
git pull && docker compose up -d --build

# Check certificate expiration
openssl x509 -in tak/certs/files/ca.pem -noout -dates
```

---

## 🎉 Deployment Complete!

Your TAK server is now running on AWS EC2 with:
- ✅ Professional hosting infrastructure
- ✅ Scalable configuration
- ✅ Secure SSL/TLS connections
- ✅ Automated backups
- ✅ Health monitoring
- ✅ Cost optimization

**Access your server at:** `https://your-domain.com:8443`

**Next Steps:**
1. Create user accounts in the web interface
2. Generate client certificates for your team
3. Configure ATAK/iTAK clients
4. Set up monitoring dashboards
5. Plan scaling strategy

---

**⚠️ Security Notes:**
- Change default passwords immediately
- Regularly update certificates
- Monitor access logs
- Keep Docker images updated
- Use VPN for sensitive operations

**📞 Support:**
- [TAK Product Center](https://github.com/TAK-Product-Center/Server)
- [Cloud-RF TAK Server](https://github.com/Cloud-RF/tak-server)
- [AWS Documentation](https://docs.aws.amazon.com/ec2/)