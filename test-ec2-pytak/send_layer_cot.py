#!/usr/bin/env python3

import asyncio
import ssl
import os
import uuid
from datetime import datetime, timezone

async def send_layer_cot():
    tak_host = "10.212.2.206"
    tak_port = 8089
    
    cert_dir = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/"
    client_cert = os.path.join(cert_dir, "user_pytac_mac.pem")
    client_key = os.path.join(cert_dir, "user_pytac_mac.key")
    ca_cert = os.path.join(cert_dir, "ca.pem")
    
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_verify_locations(ca_cert)
    ssl_context.load_cert_chain(client_cert, client_key, password="atakatak")
    
    reader, writer = await asyncio.open_connection(tak_host, tak_port, ssl=ssl_context)
    
    # Create proper CoT XML for map layer
    
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    stale_time = datetime.fromtimestamp(now.timestamp() + 86400, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    uid = f"MAP-LAYER-{uuid.uuid4().hex[:8]}"
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="b-i-v" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="37.7749" lon="-122.4194" hae="0.0" ce="10" le="10"/>
    <detail>
        <contact callsign="Bing Hybrid Layer"/>
        <remarks>Custom map layer - Bing Hybrid tiles</remarks>
        <archive/>
        <mapLayer>
            <name>Bing - Hybrid</name>
            <minZoom>0</minZoom>
            <maxZoom>20</maxZoom>
            <tileType>png</tileType>
            <url>https://ecn.t2.tiles.virtualearth.net/tiles/h{{$q}}?g=761&amp;mkt=en-us</url>
            <tileUpdate>None</tileUpdate>
            <backgroundColor>#000000</backgroundColor>
            <ignoreErrors>false</ignoreErrors>
        </mapLayer>
    </detail>
</event>'''
    
    writer.write(cot_xml.encode('utf-8'))
    await writer.drain()
    await asyncio.sleep(1)
    writer.close()

if __name__ == "__main__":
    asyncio.run(send_layer_cot())