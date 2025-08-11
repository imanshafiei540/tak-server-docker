#!/bin/bash

# Create iPhone data package for TAK server
IP="10.100.110.18"
USER="iPhone"

echo "Creating iPhone data package for TAK server at $IP"

# Create server.pref with correct IP
cat > server.pref << EOF
<?xml version='1.0' encoding='ASCII' standalone='yes'?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">TAK Server</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">$IP:8089:ssl</entry>
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

# Create manifest.xml
cat > manifest.xml << EOF
<MissionPackageManifest version="2">
  <Configuration>
    <Parameter name="uid" value="iPhone-TAK-Setup"/>
    <Parameter name="name" value="$USER DP"/>
    <Parameter name="onReceiveDelete" value="true"/>
  </Configuration>
  <Contents>
    <Content ignore="false" zipEntry="certs\\server.pref"/>
    <Content ignore="false" zipEntry="certs\\192.168.65.1.p12"/>
    <Content ignore="false" zipEntry="certs\\$USER.p12"/>
  </Contents>
</MissionPackageManifest>
EOF

# Create the zip package
zip -j tak/certs/files/$USER-$IP.dp.zip manifest.xml server.pref tak/certs/files/192.168.65.1.p12 tak/certs/files/$USER.p12

# Clean up temp files
rm manifest.xml server.pref

echo "-------------------------------------------------------------"
echo "✅ Created iPhone data package: tak/certs/files/$USER-$IP.dp.zip"
echo "📱 This package contains:"
echo "   - Server configuration for $IP:8089"
echo "   - Server certificate (192.168.65.1.p12)"
echo "   - Client certificate ($USER.p12)"
echo "   - Password for all certificates: atakatak" 