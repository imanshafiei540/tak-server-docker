# TAK Server & Marker Creation Guide for macOS Apple Silicon

> **Tested on:** macOS Apple Silicon (M1/M2/M3), but should work on other platforms

This guide walks you through setting up a complete TAK (Team Awareness Kit) server environment and programmatically sending markers to the map. Despite TAK documentation suggesting it doesn't work on Mac, we've successfully deployed and tested it.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial TAK Server Setup](#initial-tak-server-setup)
3. [Certificate Configuration](#certificate-configuration)
4. [The Challenge: Sending Markers](#the-challenge-sending-markers)
5. [The Solution: PyTAK Library](#the-solution-pytak-library)
6. [Testing Your Setup](#testing-your-setup)
7. [Creating Custom Markers](#creating-custom-markers)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

## 🔧 Prerequisites

### System Requirements
- macOS with Apple Silicon (M1/M2/M3) - *tested platform*
- Docker Desktop for Mac
- Python 3.8+
- Terminal access
- At least 4GB RAM free
- Network connection

### Software Installation

```bash
# Install Docker Desktop for Mac
# Download from: https://www.docker.com/products/docker-desktop/

# Verify Docker installation
docker --version
docker compose version

# Install required Python packages (we'll do this later)
# pip3 install pytak
```

## 🚀 Initial TAK Server Setup

### Step 1: Download Official TAK Release

1. Register at [tak.gov](https://tak.gov/)
2. Download `takserver-docker-5.4-RELEASE-19.zip` (or latest version)
3. Place the ZIP file in your project directory

### Step 2: Clone and Setup Project

```bash
# Clone the TAK server Docker wrapper
git clone https://github.com/Cloud-RF/tak-server.git
cd tak-server

# Copy your downloaded TAK release to this directory
cp ~/Downloads/takserver-docker-5.4-RELEASE-19.zip .
```

### Step 3: Create Environment Configuration

```bash
# Create .env file for certificate generation
cat << EOF > .env
COUNTRY=US
STATE=CA
CITY=San Francisco
ORGANIZATIONAL_UNIT=TAK
EOF
```

### Step 4: Configure TAK Server

```bash
# Copy the provided CoreConfig.xml or edit it
# Update IP address to match your Docker environment
# For macOS, typically use: 192.168.65.1
```

Example `CoreConfig.xml` key settings:
```xml
<!-- SSL/TLS port for TAK clients -->
<input _name="stdssl" protocol="tls" port="8089"/>

<!-- Web interface ports -->
<connector port="8443" _name="https"/>
<connector port="8446" clientAuth="false" _name="cert_https"/>

<!-- Database connection -->
<connection url="jdbc:postgresql://tak-database:5432/cot" username="martiuser" password="YOUR_DB_PASSWORD"/>
```

### Step 5: Run Setup Script

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run the setup (this will take several minutes)
./scripts/setup.sh
```

**Expected Output:**
- Container builds and starts
- Certificates are generated automatically
- Random passwords are created
- Server becomes accessible at `https://192.168.65.1:8443`

### Step 6: Verify Installation

```bash
# Check containers are running
docker ps

# Should see both tak-server-docker-tak-1 and tak-server-docker-db-1

# Test web access
curl -k https://192.168.65.1:8443
```

## 🔐 Certificate Configuration

The setup script automatically creates:

```
tak/certs/files/
├── admin.p12           # Admin browser certificate
├── user1.p12          # Client certificate  
├── user2.p12          # Additional client certificate
├── ca.pem             # Certificate Authority
├── admin.pem          # Admin certificate (PEM format)
├── user1.pem          # User certificate (PEM format)
├── user1.key          # User private key
└── ...
```

### Import Admin Certificate to Browser

1. Copy `admin.p12` from `tak/certs/files/`
2. Import to your browser:
   - **Chrome:** Settings → Privacy & Security → Security → Manage Certificates
   - **Firefox:** Settings → Privacy & Security → Certificates → View Certificates
3. Use password: `atakatak`
4. Access: https://192.168.65.1:8443

## 🎯 The Challenge: Sending Markers

Initially, we discovered that:
- ❌ WebTAK is primarily for viewing, not creating markers
- ❌ Simple HTTP API calls don't work due to SSL requirements
- ❌ CoT injector endpoints are for scheduled messages, not real-time
- ❌ Port 8089 requires authenticated TAK clients, not raw TCP

### Failed Approaches We Tried

1. **HTTP API via Swagger** (`https://192.168.65.1:8446/swagger-ui/`)
2. **CoT Injector endpoint** (`/Marti/api/injectors/cot/uid`)
3. **Raw TCP to port 8089** (`echo 'XML' | nc 192.168.65.1 8089`)
4. **Simple Python libraries** without SSL support

## ✅ The Solution: PyTAK Library

We found that [PyTAK](https://github.com/snstac/pytak) is the professional-grade solution for TAK integration.

### Install PyTAK

```bash
# Install the PyTAK library
pip3 install pytak
```

### Our Working Scripts

We created several Python scripts that successfully send markers:

1. **`pytak_final.py`** - Complete working solution with SSL
2. **`create_your_markers.py`** - Template for custom markers

## 🧪 Testing Your Setup

### Test 1: Basic Connectivity

```bash
# Test if TAK server is accessible
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('192.168.65.1', 8089))
print('✅ Connected' if result == 0 else '❌ Connection failed')
sock.close()
"
```

### Test 2: Send Test Markers

```bash
# Run our working script
python3 pytak_final.py
```

**Expected Output:**
```
🚀 TAK Server Marker Sender
========================================
✅ Basic TCP connectivity confirmed
🎉 Connected to TAK server with SSL client authentication!
📍 Sending marker 1/4: Python Test 1
📍 Sending marker 2/4: Python Test 2
📍 Sending marker 3/4: Emergency
📍 Sending marker 4/4: Vehicle-1
🎯 All markers sent successfully!
```

### Test 3: Verify in WebTAK

1. Open browser with admin certificate installed
2. Go to: https://192.168.65.1:8443/webtak/index.html
3. Look for the markers on the map

## 🎨 Creating Custom Markers

### Method 1: Edit the Template

```bash
# Edit the custom marker script
nano create_your_markers.py

# Modify the markers array:
your_markers = [
    {
        "uid": "my-location",
        "lat": 37.7749,         # Your latitude
        "lon": -122.4194,       # Your longitude
        "callsign": "My Position",
        "type": "a-f-G-U-C",    # Friendly ground unit
        "remarks": "This is my location!"
    },
    # Add more markers...
]

# Run it
python3 create_your_markers.py
```

### Method 2: Command Line Script

Create a simple command-line tool:

```python
#!/usr/bin/env python3
import sys
import asyncio
# ... (use the functions from pytak_final.py)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 send_marker.py <lat> <lon> <callsign> <remarks>")
        sys.exit(1)
    
    lat, lon, callsign, remarks = sys.argv[1:5]
    marker = {
        "uid": f"cli-{callsign}",
        "lat": float(lat),
        "lon": float(lon),
        "callsign": callsign,
        "type": "a-f-G-U-C",
        "remarks": remarks
    }
    # Send single marker...
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

## 🔧 Troubleshooting

### Common Issues

#### "Connection Refused"
```bash
# Check if containers are running
docker ps

# Restart if needed
docker compose down
docker compose up -d

# Check logs
docker logs tak-server-docker-tak-1
```

#### "SSL Handshake Failure"
```bash
# Verify certificate files exist
ls -la tak/certs/files/user1.*

# Regenerate if missing
docker exec -it tak-server-docker-tak-1 bash -c "cd /opt/tak/certs && ./makeCert.sh client user1"
```

#### "Certificate Authentication Failed"
```bash
# Check certificate permissions
chmod 644 tak/certs/files/user1.pem
chmod 600 tak/certs/files/user1.key

# Verify certificate content
openssl x509 -in tak/certs/files/user1.pem -text -noout
```

#### "Markers Not Appearing"
1. Check WebTAK at: https://192.168.65.1:8443/webtak/index.html
2. Verify you have admin certificate installed in browser
3. Check TAK server logs for CoT message reception
4. Ensure marker coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)

### Debug Commands

```bash
# Check TAK server logs
docker exec -it tak-server-docker-tak-1 tail -f /opt/tak/logs/takserver.log

# Check network connectivity
netstat -an | grep 8089

# Test SSL connection
openssl s_client -connect 192.168.65.1:8089 -cert tak/certs/files/user1.pem -key tak/certs/files/user1.key

# Check certificate chain
openssl verify -CAfile tak/certs/files/ca.pem tak/certs/files/user1.pem
```

## 🚀 Advanced Usage

### Integration with Real GPS Data

```python
# Example: Read GPS from file and send as markers
import json

def send_gps_track(gps_file):
    with open(gps_file, 'r') as f:
        points = json.load(f)
    
    for point in points:
        marker = {
            "uid": f"gps-{point['timestamp']}",
            "lat": point['lat'],
            "lon": point['lon'],
            "callsign": f"Track Point {point['id']}",
            "type": "a-f-G-U-C",
            "remarks": f"GPS point at {point['timestamp']}"
        }
        # Send marker...
```

### Automated Marker Updates

```python
# Example: Update marker position every 10 seconds
import asyncio

async def update_moving_marker():
    while True:
        # Calculate new position
        # Send updated marker with same UID
        await asyncio.sleep(10)
```

### Mission Integration

```python
# Example: Send markers to specific mission
def create_mission_marker(mission_name, marker_data):
    # Add mission-specific details to marker
    marker_data["detail"]["mission"] = mission_name
    return marker_data
```

## 📚 Resources

- **TAK Server Documentation:** [GitHub TAK Product Center](https://github.com/TAK-Product-Center/Server)
- **PyTAK Library:** [https://github.com/snstac/pytak](https://github.com/snstac/pytak)
- **CoT Specification:** [MITRE MP090284](https://www.mitre.org/publications/technical-papers/cursor-on-target)
- **TAK Server Docker:** [Cloud-RF/tak-server](https://github.com/Cloud-RF/tak-server)

## 🎉 Success Checklist

- [ ] TAK server running on Docker
- [ ] WebTAK accessible at https://192.168.65.1:8443
- [ ] Admin certificate installed in browser
- [ ] PyTAK library installed
- [ ] `pytak_final.py` script runs successfully
- [ ] Test markers visible in WebTAK
- [ ] Custom markers script created and tested

## 💡 Tips for macOS Apple Silicon

1. **Docker Performance:** Allocate at least 4GB RAM to Docker Desktop
2. **Network Issues:** Use `192.168.65.1` for Docker host IP on Mac
3. **Certificate Issues:** macOS Keychain may interfere; use Firefox for testing
4. **File Permissions:** Use `chmod 644` for .pem files, `chmod 600` for .key files
5. **Python Environment:** Consider using virtual environments for package isolation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install pytak
```

---

**🎯 You now have a complete TAK server environment with programmatic marker creation capabilities!**

This setup enables you to:
- Run a professional TAK server
- Send markers from Python scripts
- Integrate with external data sources
- Build custom TAK applications
- Test TAK workflows without expensive TAK server licenses

**Next Steps:** Explore the PyTAK documentation for advanced features like file sharing, mission management, and real-time data streaming. 