#!/bin/bash

# Create Mac client data package for PlayCover ATAK or desktop TAK clients
LOCAL_IP="127.0.0.1"        # Localhost for PlayCover
LAN_IP="192.168.65.1"       # Docker IP for desktop clients
USER="MacClient"

echo "Creating Mac client data package for local TAK clients..."

# Create server.pref with localhost for PlayCover
cat > server_localhost.pref << EOF
<?xml version='1.0' encoding='ASCII' standalone='yes'?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">TAK Server (Localhost)</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">$LOCAL_IP:8089:ssl</entry>
  </preference>
  <preference version="1" name="com.atakmap.app_preferences">
    <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
    <entry key="caLocation" class="class java.lang.String">cert/192.168.65.1.p12</entry>
    <entry key="caPassword" class="class java.lang.String">atakatak</entry>
    <entry key="clientPassword" class="class java.lang.String">atakatak</entry>
    <entry key="certificateLocation" class="class java.lang.String">cert/$USER.p12</entry>
  </preference>
</preferences>
EOF

# Create server.pref with Docker IP for desktop clients
cat > server_docker.pref << EOF
<?xml version='1.0' encoding='ASCII' standalone='yes'?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">TAK Server (Docker)</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">$LAN_IP:8089:ssl</entry>
  </preference>
  <preference version="1" name="com.atakmap.app_preferences">
    <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
    <entry key="caLocation" class="class java.lang.String">cert/192.168.65.1.p12</entry>
    <entry key="caPassword" class="class java.lang.String">atakatak</entry>
    <entry key="clientPassword" class="class java.lang.String">atakatak</entry>
    <entry key="certificateLocation" class="class java.lang.String">cert/$USER.p12</entry>
  </preference>
</preferences>
EOF

# Create manifest for localhost package
cat > manifest_localhost.xml << EOF
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="MacClient-Localhost-Setup"/>
    <Parameter name="name" value="$USER Localhost DP"/>
    <Parameter name="onReceiveDelete" value="true"/>
  </Configuration>
  <Contents>
    <Content ignore="false" zipEntry="certs\\server_localhost.pref"/>
    <Content ignore="false" zipEntry="certs\\192.168.65.1.p12"/>
    <Content ignore="false" zipEntry="certs\\$USER.p12"/>
  </Contents>
</MissionPackageManifest>
EOF

# Create manifest for Docker IP package
cat > manifest_docker.xml << EOF
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="MacClient-Docker-Setup"/>
    <Parameter name="name" value="$USER Docker DP"/>
    <Parameter name="onReceiveDelete" value="true"/>
  </Configuration>
  <Contents>
    <Content ignore="false" zipEntry="certs\\server_docker.pref"/>
    <Content ignore="false" zipEntry="certs\\192.168.65.1.p12"/>
    <Content ignore="false" zipEntry="certs\\$USER.p12"/>
  </Contents>
</MissionPackageManifest>
EOF

# Create packages
echo "Creating localhost package (for PlayCover ATAK)..."
zip -j tak/certs/files/$USER-localhost.dp.zip manifest_localhost.xml server_localhost.pref tak/certs/files/192.168.65.1.p12 tak/certs/files/$USER.p12

echo "Creating Docker IP package (for desktop TAK clients)..."
zip -j tak/certs/files/$USER-docker.dp.zip manifest_docker.xml server_docker.pref tak/certs/files/192.168.65.1.p12 tak/certs/files/$USER.p12

# Clean up temp files
rm manifest_localhost.xml manifest_docker.xml server_localhost.pref server_docker.pref

echo "-------------------------------------------------------------"
echo "✅ Created Mac client packages:"
echo "📦 tak/certs/files/$USER-localhost.dp.zip (for PlayCover ATAK)"
echo "📦 tak/certs/files/$USER-docker.dp.zip (for desktop TAK clients)"
echo ""
echo "🎮 PlayCover ATAK Setup:"
echo "1. Install PlayCover from GitHub"
echo "2. Install ATAK via PlayCover"
echo "3. Import $USER-localhost.dp.zip into ATAK"
echo "4. Server will connect to 127.0.0.1:8089"
echo ""
echo "🖥️  Desktop TAK Client Setup:"
echo "1. Import $USER-docker.dp.zip"
echo "2. Server will connect to 192.168.65.1:8089"
echo ""
echo "🔑 Certificate password: atakatak" 