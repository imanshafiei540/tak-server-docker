#!/usr/bin/env python3
"""
Test localhost connectivity for PlayCover ATAK
"""

import asyncio
import ssl
import os
from datetime import datetime, timezone

async def test_localhost_connection():
    """Test TAK server via localhost (for PlayCover)"""
    
    tak_host = "127.0.0.1"  # Localhost for PlayCover
    tak_port = 8089
    
    cert_dir = "tak/certs/files"
    client_cert = os.path.join(cert_dir, "MacClient.pem")
    client_key = os.path.join(cert_dir, "MacClient.key")
    ca_cert = os.path.join(cert_dir, "ca.pem")
    
    print(f"🏠 Testing localhost connection for PlayCover ATAK...")
    print(f"📡 Connecting to {tak_host}:{tak_port}")
    
    # SSL setup
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_verify_locations(ca_cert)
    ssl_context.load_cert_chain(client_cert, client_key)
    
    try:
        reader, writer = await asyncio.open_connection(tak_host, tak_port, ssl=ssl_context)
        print("✅ Localhost connection successful!")
        print("🎮 PlayCover ATAK should be able to connect!")
        
        # Send a test marker
        marker = {
            "uid": "localhost-test",
            "lat": 37.7749,
            "lon": -122.4194,
            "callsign": "Localhost Test",
            "type": "a-f-G-U-C",
            "remarks": "🏠 Test from localhost - PlayCover ready!"
        }
        
        cot_xml = create_cot_xml(marker)
        writer.write(cot_xml.encode('utf-8'))
        await writer.drain()
        
        print("📍 Sent test marker for PlayCover verification")
        
        writer.close()
        await writer.wait_closed()
        return True
        
    except Exception as e:
        print(f"❌ Localhost connection failed: {e}")
        return False

def create_cot_xml(marker):
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{marker['uid']}" type="{marker['type']}" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{marker['lat']}" lon="{marker['lon']}" hae="0" ce="10" le="10"/>
    <detail>
        <contact callsign="{marker['callsign']}" endpoint="*:-1:stcp"/>
        <remarks>{marker['remarks']}</remarks>
        <precisionlocation geopointsrc="GPS" altsrc="GPS"/>
    </detail>
</event>'''

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_localhost_connection())
    loop.close() 