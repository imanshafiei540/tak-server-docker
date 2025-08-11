# Connect to EC2 TAK Server with PyTAK

> **Test marker sending to your EC2 TAK server from your local machine**

This directory contains everything you need to send markers to your EC2 TAK server from your local development environment.

## 🎯 Quick Start

1. **Copy certificates from EC2**
2. **Install Python dependencies**
3. **Update IP address**
4. **Run the script**

## 📋 Prerequisites

- Python 3.8+
- Your EC2 TAK server running
- SSH access to your EC2 instance

## 🔐 Step 1: Copy Certificates from EC2

### Create client certificates on EC2 (if needed)

SSH to your EC2 instance and create a client user:

```bash
# SSH to EC2
ssh -i your-key.pem ubuntu@10.212.2.206

# Go to TAK server directory
cd ~/tak-server

# Create new client certificate (if user1 doesn't exist)
docker exec -it tak-server-tak-1 bash -c "cd /opt/tak/certs && ./makeCert.sh client user1"

# Verify certificates exist
ls -la tak/certs/files/user1.*
```

### Download certificates to local machine

From your **local machine**, run these commands:

```bash
# Navigate to this directory
cd test-ec2-pytak

# Copy required certificates from EC2
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/user1.pem ./certs/
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/user1.key ./certs/
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/ca.pem ./certs/

# Verify certificates were copied
ls -la certs/
```

You should see:
```
certs/
├── ca.pem     # Certificate Authority
├── user1.pem  # Client certificate
└── user1.key  # Client private key
```

## 🐍 Step 2: Install Python Dependencies

```bash
# Install PyTAK library
pip3 install pytak

# Or if using virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pytak
```

## ⚙️ Step 3: Update Configuration

Edit `pytak_test_ec2.py` and update the IP address:

```python
# Change this line to your EC2 public IP
tak_host = "10.212.2.206"  # Replace with YOUR EC2 IP
```

## 🚀 Step 4: Run the Test

```bash
# Run the marker sender
python3 pytak_test_ec2.py
```

**Expected Output:**
```
🚀 EC2 TAK Server Marker Sender
========================================
🎯 Target: 10.212.2.206:8089
📂 Make sure certificates are in ./certs/ directory

✅ Basic TCP connectivity confirmed to 10.212.2.206:8089
🚀 Connecting to TAK server at 10.212.2.206:8089
📜 Using client cert: certs/user1.pem
🔑 Using client key: certs/user1.key
🏛️  Using CA cert: certs/ca.pem
✅ SSL context configured successfully
🎉 Connected to TAK server with SSL client authentication!
📍 Sending marker 1/4: Python Test 1
📍 Sending marker 2/4: Python Test 2
📍 Sending marker 3/4: Emergency
📍 Sending marker 4/4: Vehicle-1

🎯 All markers sent successfully!
🌐 Check your WebTAK: https://10.212.2.206:8443/webtak/index.html
📱 Or check ATAK/iTAK clients connected to the server

🎉 Mission accomplished! Your markers should now be visible in EC2 TAK clients.
```

## 📱 Step 5: Verify Markers

### WebTAK (Browser)
1. Import `admin.p12` certificate to browser (password: `atakatak`)
2. Go to: `https://10.212.2.206:8443/webtak/index.html`
3. Look for the test markers on the map

### ATAK/iTAK Clients
Your test markers should appear on connected mobile devices.

## 🔧 Troubleshooting

### "Certificate file not found"
```bash
# Check certificates exist
ls -la certs/

# Re-copy from EC2 if missing
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/*.pem ./certs/
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/user1.key ./certs/
```

### "Connection refused"
```bash
# Check EC2 security groups allow port 8089
# Verify TAK server is running on EC2
ssh -i your-key.pem ubuntu@10.212.2.206 "docker ps"
```

### "SSL handshake failure"
```bash
# Check certificate permissions
chmod 644 certs/*.pem
chmod 600 certs/*.key

# Verify certificate validity
openssl x509 -in certs/user1.pem -text -noout
```

### "No module named 'pytak'"
```bash
# Install pytak
pip3 install pytak

# Or check Python environment
python3 -c "import pytak; print('PyTAK installed successfully')"
```

## 🎨 Customizing Markers

Edit the `markers` array in `pytak_test_ec2.py`:

```python
markers = [
    {
        "uid": "my-custom-marker",
        "lat": 37.7749,         # Your latitude
        "lon": -122.4194,       # Your longitude  
        "callsign": "My Location",
        "type": "a-f-G-U-C",    # Friendly ground unit
        "remarks": "Custom marker from Python!"
    }
    # Add more markers...
]
```

### CoT Type Reference
```
a-f-G-U-C     = Friendly ground unit (blue)
a-n-G-U-C     = Neutral ground unit (green) 
a-h-G-U-C     = Hostile ground unit (red)
a-f-G-E-V-C   = Friendly vehicle (blue vehicle)
a-u-G-U-C     = Unknown ground unit (yellow)
a-f-A-M-F-Q   = Friendly aircraft (blue aircraft)
```

## 📂 Directory Structure

```
test-ec2-pytak/
├── HOW_TO_CONNECT_EC2.md     # This file
├── pytak_test_ec2.py         # Main test script
└── certs/                    # Certificates (you copy these)
    ├── ca.pem               # Certificate Authority
    ├── user1.pem            # Client certificate
    └── user1.key            # Client private key
```

## 🔄 Commands Summary

```bash
# 1. Copy certificates from EC2
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/user1.pem ./certs/
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/user1.key ./certs/
scp -i your-key.pem ubuntu@10.212.2.206:~/tak-server/tak/certs/files/ca.pem ./certs/

# 2. Install dependencies
pip3 install pytak

# 3. Update IP in script (edit pytak_test_ec2.py)

# 4. Run test
python3 pytak_test_ec2.py

# 5. Check results at:
# https://10.212.2.206:8443/webtak/index.html
```

---

## 🎉 Success!

If everything works, you now have:
- ✅ Local Python script connecting to EC2 TAK server
- ✅ SSL client authentication working
- ✅ Test markers visible in WebTAK/ATAK
- ✅ Foundation for custom TAK applications

**Next Steps:**
- Integrate with real GPS data
- Create automated marker updates
- Build custom TAK client applications
- Add mission-specific marker types

---

**📞 Need Help?**
- Check the main [AWS_EC2_DEPLOYMENT.md](../AWS_EC2_DEPLOYMENT.md) guide
- Verify your EC2 TAK server logs: `docker logs -f tak-server-tak-1`
- Test basic connectivity: `telnet 10.212.2.206 8089`