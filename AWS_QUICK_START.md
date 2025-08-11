# TAK Server AWS EC2 Quick Start

> **Get your TAK server running on AWS in 15 minutes**

## 🎯 Quick Reference

### **Recommended AWS Configuration**
- **OS:** Ubuntu 22.04 LTS 
- **Instance:** t3.large (2 vCPU, 8GB RAM)
- **Storage:** 50GB GP3 SSD
- **Monthly Cost:** ~$60

### **Required Security Group Ports**
```
22   (SSH - restrict to your IP)
8089 (TAK Client SSL)
8443 (Web Interface)
8444 (Certificate Auth)
8446 (API Access)
9000 (Streaming)
9001 (Federation)
```

## 🚀 Fastest Deployment Path

### 1. Launch EC2 Instance
- Choose Ubuntu 22.04 LTS AMI
- Select t3.large instance type
- Configure security group with ports above
- Assign Elastic IP (recommended)

### 2. Connect and Deploy
```bash
# SSH to your instance
ssh -i your-key.pem ubuntu@YOUR.EC2.IP

# Clone repository
git clone https://github.com/Cloud-RF/tak-server.git
cd tak-server

# Upload your TAK release ZIP file here
# (download from https://tak.gov/products/tak-server)

# Run automated deployment script
chmod +x deploy-to-aws.sh
./deploy-to-aws.sh
```

### 3. Access Your Server
- **Web Interface:** `https://YOUR.EC2.IP:8443`
- **Certificate:** Import `admin.p12` from `tak/certs/files/`
- **Password:** `atakatak`

## 📱 Connect ATAK/iTAK Clients

1. Download client certificates from web interface
2. Configure in ATAK:
   - **Server:** YOUR.EC2.IP
   - **Port:** 8089
   - **Protocol:** SSL

## 🔧 Essential Commands

```bash
# Check status
docker ps

# View logs
docker logs -f tak-server-tak-1

# Restart service
docker compose restart

# Manual backup
./backup-tak.sh

# Check certificates
ls -la tak/certs/files/
```

## 🔐 Security Checklist

- [ ] Change default admin password
- [ ] Restrict SSH to your IP only
- [ ] Use strong certificate passwords
- [ ] Enable automated backups
- [ ] Monitor access logs
- [ ] Keep system updated

## 💰 Cost Estimates (us-east-1)

| Instance Type | Monthly Cost | Suitable For |
|---------------|--------------|--------------|
| t3.medium     | ~$30        | 1-10 users   |
| t3.large      | ~$60        | 10-50 users  |
| t3.xlarge     | ~$120       | 50-200 users |

*Plus storage (~$5/month for 50GB) and data transfer costs*

## 🆘 Troubleshooting

**Connection refused?**
- Check security groups allow the ports
- Verify containers are running: `docker ps`

**SSL errors?**
- Import correct certificates to browser
- Check certificate expiration dates

**Performance issues?**
- Monitor resources: `docker stats`
- Consider upgrading instance type

## 📞 Support Resources

- **Full Guide:** [AWS_EC2_DEPLOYMENT.md](AWS_EC2_DEPLOYMENT.md)
- **TAK Docs:** [https://github.com/TAK-Product-Center/Server](https://github.com/TAK-Product-Center/Server)
- **Issues:** [https://github.com/Cloud-RF/tak-server/issues](https://github.com/Cloud-RF/tak-server/issues)

---

**🎉 That's it! Your TAK server should now be running on AWS EC2 with professional hosting capabilities.**