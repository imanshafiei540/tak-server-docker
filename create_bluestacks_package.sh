#!/bin/bash

# Create BlueStacks ATAK data package
BLUESTACKS_IP="10.100.110.18"    # LAN IP accessible from BlueStacks
USER="BlueStacks"

echo "🎮 Creating BlueStacks ATAK data package..."
echo "🌐 Server IP: $BLUESTACKS_IP"
echo "👤 User: $USER"

# Create server.pref for BlueStacks ATAK
cat > server_bluestacks.pref << EOF
<?xml version='1.0' encoding='ASCII' standalone='yes'?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">TAK Server (BlueStacks)</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">$BLUESTACKS_IP:8089:ssl</entry>
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

# Create manifest.xml for BlueStacks
cat > manifest_bluestacks.xml << EOF
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="BlueStacks-ATAK-Setup"/>
    <Parameter name="name" value="$USER DP"/>
    <Parameter name="onReceiveDelete" value="true"/>
  </Configuration>
  <Contents>
    <Content ignore="false" zipEntry="certs\\server_bluestacks.pref"/>
    <Content ignore="false" zipEntry="certs\\192.168.65.1.p12"/>
    <Content ignore="false" zipEntry="certs\\$USER.p12"/>
  </Contents>
</MissionPackageManifest>
EOF

# Generate BlueStacks client certificate if it doesn't exist
if [ ! -f "tak/certs/files/$USER.p12" ]; then
    echo "🔐 Generating $USER client certificate..."
    docker exec -it tak-server-docker-tak-1 bash -c "cd /opt/tak/certs && ./makeCert.sh client $USER"
    docker exec -it tak-server-docker-tak-1 bash -c "chown -R 1000:1000 /opt/tak/certs/"
fi

# Create the data package
echo "📦 Creating BlueStacks data package..."
zip -j tak/certs/files/$USER-$BLUESTACKS_IP.dp.zip manifest_bluestacks.xml server_bluestacks.pref tak/certs/files/192.168.65.1.p12 tak/certs/files/$USER.p12

# Clean up temp files
rm manifest_bluestacks.xml server_bluestacks.pref

echo "-------------------------------------------------------------"
echo "✅ Created BlueStacks data package: tak/certs/files/$USER-$BLUESTACKS_IP.dp.zip"
echo ""
echo "🎮 BlueStacks ATAK Setup Instructions:"
echo "1. Install BlueStacks from https://www.bluestacks.com/"
echo "2. Download ATAK-CIV APK from civtak.org or APKPure"
echo "3. Install APK in BlueStacks (drag & drop or sideload)"
echo "4. Import data package: $USER-$BLUESTACKS_IP.dp.zip"
echo "5. Server will connect to: $BLUESTACKS_IP:8089"
echo ""
echo "📱 Alternative: Install directly from Google Play Store in BlueStacks"
echo "🔑 Certificate password: atakatak"
echo ""
echo "🧪 Test connection with: python3 pytak_lan.py" 