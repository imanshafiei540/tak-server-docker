import asyncio
import ssl
import os
from datetime import datetime, timezone

async def send_markers_to_tak():
    tak_host = "10.212.2.206"
    tak_port = 8089

    cert_dir = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/"
    client_cert = os.path.join(cert_dir, "user_pytac_mac.pem")
    client_key = os.path.join(cert_dir, "user_pytac_mac.key")
    ca_cert = os.path.join(cert_dir, "ca.pem")
    
    for cert_file in [client_cert, client_key, ca_cert]:
        if not os.path.exists(cert_file):
            return False
    
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        ssl_context.load_verify_locations(ca_cert)
        ssl_context.load_cert_chain(client_cert, client_key, password="atakatak")
        
    except Exception as e:
        return False
    
    try:
        reader, writer = await asyncio.open_connection(
            tak_host, tak_port, ssl=ssl_context
        )
        
        markers = [
            {
                "uid": "python-marker-unique-1",
                "lat": 37.7700,
                "lon": -122.4150,
                "callsign": "Python Test 1",
                "type": "a-f-G-U-C",
                "remarks": "Marker sent from Python script"
            },
            {
                "uid": "python-marker-2",
                "lat": 37.7849,
                "lon": -122.4094,
                "callsign": "Python Test 2", 
                "type": "a-n-G-U-C",
                "remarks": "Second test marker with PyTAK"
            },
            {
                "uid": "emergency-test",
                "lat": 37.7649,
                "lon": -122.4294,
                "callsign": "Emergency",
                "type": "a-h-G-U-C",
                "remarks": "Emergency test marker"
            },
            {
                "uid": "vehicle-marker",
                "lat": 37.7549,
                "lon": -122.4394,
                "callsign": "Vehicle-1",
                "type": "a-f-G-E-V-C",
                "remarks": "Test vehicle marker"
            },
            {
                "uid": "test-area-point",
                "lat": 37.7650,
                "lon": -122.4300,
                "callsign": "Test Area Point",
                "type": "b-m-p-w",
                "remarks": "Test area marker as point"
            },

        ]
        for i, marker in enumerate(markers, 1):
            cot_xml = create_cot_xml(marker)
            writer.write(cot_xml.encode('utf-8'))
            await writer.drain()
            await asyncio.sleep(1)
        
        test_polygon = {
            "uid": "test-polygon-direct",
            "callsign": "TestPolygon",
            "remarks": "Direct XML polygon test",
            "coordinates": [
                [37.7700, -122.4200],
                [37.7750, -122.4200],
                [37.7750, -122.4150],
                [37.7700, -122.4150],
                [37.7700, -122.4200]
            ]
        }
        
        polygon_xml = create_simple_polygon_cot_xml(test_polygon)
        writer.write(polygon_xml.encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1)
        test_line = {
            "uid": "test-line-direct",
            "callsign": "TestLine",
            "remarks": "Direct XML line test",
            "coordinates": [
                [37.7600, -122.4300],
                [37.7650, -122.4250],
                [37.7700, -122.4200],
                [37.7750, -122.4150]
            ]
        }
        
        line_xml = create_line_cot_xml(test_line)
        writer.write(line_xml.encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1)
        
        atak_rectangle = {
            "uid": "atak-rectangle-test",
            "callsign": "ATAK-Rectangle",
            "remarks": "ATAK rectangle test",
            "coordinates": [
                [37.7800, -122.4000],
                [37.7850, -122.4000],
                [37.7850, -122.3950],
                [37.7800, -122.3950],
                [37.7800, -122.4000]
            ]
        }
        
        atak_rectangle_xml = create_rectangle_cot_xml(atak_rectangle)
        writer.write(atak_rectangle_xml.encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1)
        
        atak_line = {
            "uid": "atak-line-test",
            "callsign": "ATAK-Line",
            "remarks": "ATAK line test",
            "coordinates": [
                [37.7900, -122.4100],
                [37.7920, -122.4080],
                [37.7940, -122.4060],
                [37.7960, -122.4040]
            ]
        }
        
        atak_line_xml = create_line_cot_xml(atak_line)
        writer.write(atak_line_xml.encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1)
        
        writer.close()
        await writer.wait_closed()
        
        return True
        
    except (ssl.SSLError, Exception) as e:
        return False

def create_cot_xml(marker):
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    
    stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{marker['uid']}" type="{marker['type']}" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{marker['lat']}" lon="{marker['lon']}" hae="0" ce="10" le="10"/>
    <detail>
        <contact callsign="{marker['callsign']}" endpoint="*:-1:stcp"/>
        <remarks>{marker['remarks']}</remarks>
        <precisionlocation geopointsrc="GPS" altsrc="GPS"/>
        <color argb="-1"/>
        <link type="image/tiff" relation="overlay" href="https://s3.amazonaws.com/venus-l2a-cogs/ALTAMAH/2024/03/19/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_D/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_C_V3-1_FRE_B1.tif"/>
    </detail>
</event>'''
    
    return cot_xml

def create_simple_polygon_cot_xml(polygon):
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    
    stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    center_lat = polygon.get('center_lat')
    center_lon = polygon.get('center_lon')
    
    if center_lat is None or center_lon is None:
        coords = polygon['coordinates']
        center_lat = sum(coord[0] for coord in coords) / len(coords)
        center_lon = sum(coord[1] for coord in coords) / len(coords)
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{polygon['uid']}" type="u-d-f" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{center_lat}" lon="{center_lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <shape>
            <polyline closed="true">'''
    
    for coord in polygon['coordinates']:
        cot_xml += f'''
                <vertex lat="{coord[0]}" lon="{coord[1]}" hae="0.0"/>'''
    
    cot_xml += '''
            </polyline>
        </shape>
        <labels_on>false</labels_on>
        <color value="-256"/>
        <fillColor value="-16711681"/>
        <strokeColor value="-65536"/>
        <strokeWeight value="3.0"/>
        <strokeStyle value="0"/>
        <contact callsign="''' + polygon['callsign'] + '''"/>
        <remarks>''' + polygon['remarks'] + '''</remarks>
        <archive/>
        <link type="image/tiff" relation="overlay" href="https://s3.amazonaws.com/venus-l2a-cogs/ALTAMAH/2024/03/19/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_D/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_C_V3-1_FRE_B1.tif"/>
    </detail>
</event>'''
    
    return cot_xml

def create_line_cot_xml(line_data):
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    
    stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    coords = line_data['coordinates']
    center_lat = sum(coord[0] for coord in coords) / len(coords)
    center_lon = sum(coord[1] for coord in coords) / len(coords)
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{line_data['uid']}" type="u-d-f" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{center_lat}" lon="{center_lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <shape>
            <polyline closed="false">'''
    
    for coord in line_data['coordinates']:
        cot_xml += f'''
                <vertex lat="{coord[0]}" lon="{coord[1]}" hae="0.0"/>'''
    
    cot_xml += '''
            </polyline>
        </shape>
        <strokeColor value="-65536"/>
        <strokeWeight value="3.0"/>
        <contact callsign="''' + line_data['callsign'] + '''"/>
        <remarks>''' + line_data['remarks'] + '''</remarks>
        <link type="image/tiff" relation="overlay" href="https://s3.amazonaws.com/venus-l2a-cogs/ALTAMAH/2024/03/19/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_D/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_C_V3-1_FRE_B1.tif"/>
    </detail>
</event>'''
    
    return cot_xml

def create_rectangle_cot_xml(rectangle_data):
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    
    stale_time = datetime.fromtimestamp(now.timestamp() + 86400, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    coords = rectangle_data['coordinates']
    center_lat = sum(coord[0] for coord in coords) / len(coords)
    center_lon = sum(coord[1] for coord in coords) / len(coords)
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{rectangle_data['uid']}" type="u-d-r" how="h-e" time="{time_str}" start="{time_str}" stale="{stale_str}" access="Undefined">
    <point lat="{center_lat}" lon="{center_lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <contact callsign="{rectangle_data['callsign']}"/>'''
    
    for coord in rectangle_data['coordinates'][:-1]:
        cot_xml += f'''
        <link point="{coord[0]},{coord[1]},0.0"/>'''
    
    cot_xml += '''
        <__shapeExtras cpvis="true" editable="true"/>
        <labels_on value="false"/>
        <remarks>''' + rectangle_data['remarks'] + '''</remarks>
        <archive/>
        <strokeColor value="-1"/>
        <strokeWeight value="3.0"/>
        <strokeStyle value="solid"/>
        <fillColor value="-1761607681"/>
        <link type="image/tiff" relation="overlay" href="https://s3.amazonaws.com/venus-l2a-cogs/ALTAMAH/2024/03/19/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_D/VENUS-XS_20240319-153935-000_L2A_ALTAMAH_C_V3-1_FRE_B1.tif"/>
    </detail>
</event>'''
    
    return cot_xml

async def test_connection(tak_host="10.212.2.206", tak_port=8089):
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((tak_host, tak_port))
        sock.close()
        return result == 0
    except Exception:
        return False

if __name__ == "__main__":
    tak_host = "10.212.2.206"
    tak_port = 8089
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        if loop.run_until_complete(test_connection(tak_host, tak_port)):
            loop.run_until_complete(send_markers_to_tak())
    finally:
        loop.close() 