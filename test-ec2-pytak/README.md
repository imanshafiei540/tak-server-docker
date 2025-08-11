# TAK Server EC2 Examples

This directory contains comprehensive examples for interacting with your EC2-hosted TAK Server using different approaches:

## 📁 Files Overview

### 1. `python_test_ec2.py` - Basic SSL Connection Test ✅ Enhanced
**Original file enhanced with polygon support**
- ✅ **Markers**: Sends various unit types (friendly, neutral, hostile, vehicles)
- ✅ **Polygons**: Now includes polygon area examples
- ✅ **SSL Authentication**: Uses proper client certificates
- ✅ **Connection Testing**: Verifies connectivity before sending

**Usage:**
```bash
python3 python_test_ec2.py
```

### 2. `pytak_comprehensive_example.py` - Advanced PyTAK Usage 🆕
**Professional-grade TAK integration using PyTAK library**
- 🎯 **Military Units**: Infantry, armor, air assets, medical, command posts
- 🔺 **Complex Polygons**: Operational areas, no-fly zones, landing zones
- 🎖️ **Mission Objects**: Waypoints, objectives, supply points
- 🚨 **Emergency Alerts**: Emergency notifications and alerts
- 💬 **Chat Messages**: Automated chat message sending
- 🚶 **Moving Units**: Real-time position updates simulation

**Features:**
- Uses professional PyTAK library for robust CoT handling
- Demonstrates military-standard CoT types and structures
- Includes real-time moving unit simulation
- Proper error handling and logging

**Usage:**
```bash
pip install pytak  # Install PyTAK library first
python3 pytak_comprehensive_example.py
```

### 3. `rest_api_example.py` - REST API Integration 🆕
**HTTP/HTTPS API interaction with TAK Server**
- 🌐 **REST Endpoints**: Direct API calls to TAK server
- 📋 **Mission Management**: Create, list, and manage missions
- 📦 **Data Packages**: File upload and sharing
- 📊 **Server Info**: Query server status and configuration
- 🔺 **Markers & Polygons**: Send via REST API methods

**Features:**
- Complete REST API demonstration
- Mission-based data organization
- File upload capabilities
- Server information queries
- Certificate-based authentication

**Usage:**
```bash
pip install requests urllib3
python3 rest_api_example.py
```

## 🔧 Setup Requirements

### 1. Certificates
All examples require proper certificate setup in `./certs/` directory:
```
certs/
├── user_pytac_mac.pem    # Client certificate
├── user_pytac_mac.key    # Client private key
└── ca.pem                # Certificate Authority
```

### 2. Server Configuration
Update the IP address in each file:
```python
tak_host = "10.212.2.206"  # Replace with your EC2 IP
```

### 3. Dependencies
```bash
# For PyTAK example
pip install pytak

# For REST API example  
pip install requests urllib3

# Basic examples use only standard library
```

## 📡 TAK Server Ports

- **8089**: SSL/TLS CoT connection (for python_test_ec2.py and PyTAK)
- **8446**: REST API endpoint (for rest_api_example.py)
- **8443**: WebTAK interface (for viewing results)

## 🎯 What Each Example Demonstrates

### Basic Example (`python_test_ec2.py`)
- **Best for**: Learning CoT message structure
- **Sends**: 4 markers + 1 polygon
- **Focus**: SSL connection and basic CoT XML

### PyTAK Example (`pytak_comprehensive_example.py`)
- **Best for**: Production-ready applications
- **Sends**: 15+ different object types + moving simulation
- **Focus**: Professional TAK integration with proper libraries

### REST API Example (`rest_api_example.py`)
- **Best for**: Web applications and mission management
- **Features**: Full REST API interaction, file uploads, mission management
- **Focus**: HTTP-based integration and data management

## 🌐 Viewing Results

After running any example, view results at:
- **WebTAK**: `https://your-ec2-ip:8443/webtak/index.html`
- **ATAK/iTAK**: Connect mobile clients to your server
- **WinTAK**: Connect desktop client to your server

## 🚀 Quick Start

1. **Set up certificates** (see main project README)
2. **Update IP addresses** in the Python files
3. **Choose your approach**:
   - Simple testing: `python_test_ec2.py`
   - Advanced features: `pytak_comprehensive_example.py`
   - REST integration: `rest_api_example.py`

## 🔍 Troubleshooting

### Connection Issues
- Verify EC2 security groups allow traffic on ports 8089, 8446, 8443
- Check certificate paths and permissions
- Ensure TAK server is running and accessible

### Certificate Issues
- Verify certificates are properly copied from EC2
- Check file permissions (readable by Python script)
- Ensure certificates haven't expired

### PyTAK Issues
- Install with: `pip install pytak`
- Check PyTAK documentation for additional configuration
- Verify certificate format compatibility

## 📚 Additional Resources

- [TAK Server Documentation](https://tak.gov/)
- [PyTAK Library](https://github.com/snstac/pytak)
- [CoT Specification](https://www.mitre.org/research/technology-transfer/open-source-software/cursor-on-target)
- [TAK REST API Reference](https://your-tak-server:8446/swagger-ui/)

## 🎯 Use Cases

- **Military Operations**: Unit tracking, situational awareness
- **Emergency Response**: Incident management, resource coordination  
- **Maritime Operations**: Vessel tracking, area monitoring
- **Aviation**: Flight tracking, airspace management
- **Security Operations**: Surveillance, threat tracking
- **Training & Simulation**: Exercise scenarios, tactical training