#!/usr/bin/env python3
"""
Convert KML files to CoT XML for TAK
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import uuid
import asyncio
import ssl
import os

def parse_kml_to_cot(kml_file):
    """Convert KML file to CoT XML messages"""
    
    tree = ET.parse(kml_file)
    root = tree.getroot()
    
    # Handle KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    cot_messages = []
    
    # Find all placemarks
    for placemark in root.findall('.//kml:Placemark', ns):
        name = placemark.find('kml:name', ns)
        description = placemark.find('kml:description', ns)
        
        placemark_name = name.text if name is not None else "Unknown"
        placemark_desc = description.text if description is not None else ""
        
        # Check for Point
        point = placemark.find('.//kml:Point/kml:coordinates', ns)
        if point is not None:
            coords = point.text.strip().split(',')
            lon, lat = float(coords[0]), float(coords[1])
            
            cot_xml = create_point_cot(placemark_name, lat, lon, placemark_desc)
            cot_messages.append(cot_xml)
        
        # Check for LineString
        linestring = placemark.find('.//kml:LineString/kml:coordinates', ns)
        if linestring is not None:
            coords_text = linestring.text.strip()
            coordinates = []
            for coord in coords_text.split():
                if coord.strip():
                    parts = coord.split(',')
                    coordinates.append([float(parts[1]), float(parts[0])])  # lat, lon
            
            cot_xml = create_line_cot(placemark_name, coordinates, placemark_desc)
            cot_messages.append(cot_xml)
        
        # Check for Polygon
        polygon = placemark.find('.//kml:Polygon//kml:coordinates', ns)
        if polygon is not None:
            coords_text = polygon.text.strip()
            coordinates = []
            for coord in coords_text.split():
                if coord.strip():
                    parts = coord.split(',')
                    coordinates.append([float(parts[1]), float(parts[0])])  # lat, lon
            
            cot_xml = create_rectangle_cot(placemark_name, coordinates, placemark_desc)
            cot_messages.append(cot_xml)
    
    return cot_messages

def create_point_cot(name, lat, lon, remarks):
    """Create point CoT XML"""
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    uid = str(uuid.uuid4())
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="a-f-G-U-C" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{lat}" lon="{lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <contact callsign="{name}"/>
        <remarks>{remarks}</remarks>
    </detail>
</event>'''

def create_line_cot(name, coordinates, remarks):
    """Create line CoT XML using ATAK format"""
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    stale_time = datetime.fromtimestamp(now.timestamp() + 86400, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    uid = str(uuid.uuid4())
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="u-d-f" how="h-e" time="{time_str}" start="{time_str}" stale="{stale_str}" access="Undefined">
    <point lat="{center_lat}" lon="{center_lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <contact callsign="{name}"/>'''
    
    for coord in coordinates:
        cot_xml += f'''
        <link point="{coord[0]},{coord[1]},0.0"/>'''
    
    cot_xml += f'''
        <__shapeExtras cpvis="true" editable="true"/>
        <labels_on value="false"/>
        <remarks>{remarks}</remarks>
        <archive/>
        <strokeColor value="-1"/>
        <strokeWeight value="3.0"/>
        <strokeStyle value="solid"/>
        <fillColor value="-1761607681"/>
    </detail>
</event>'''
    
    return cot_xml

def create_rectangle_cot(name, coordinates, remarks):
    """Create rectangle CoT XML using ATAK format"""
    now = datetime.now(timezone.utc)
    time_str = now.isoformat().replace('+00:00', 'Z')
    stale_time = datetime.fromtimestamp(now.timestamp() + 86400, timezone.utc)
    stale_str = stale_time.isoformat().replace('+00:00', 'Z')
    
    center_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
    center_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
    
    uid = str(uuid.uuid4())
    
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="u-d-r" how="h-e" time="{time_str}" start="{time_str}" stale="{stale_str}" access="Undefined">
    <point lat="{center_lat}" lon="{center_lon}" hae="0.0" ce="9999999.0" le="9999999.0"/>
    <detail>
        <contact callsign="{name}"/>'''
    
    for coord in coordinates[:-1]:  # Skip last duplicate point
        cot_xml += f'''
        <link point="{coord[0]},{coord[1]},0.0"/>'''
    
    cot_xml += f'''
        <__shapeExtras cpvis="true" editable="true"/>
        <labels_on value="false"/>
        <remarks>{remarks}</remarks>
        <archive/>
        <strokeColor value="-1"/>
        <strokeWeight value="3.0"/>
        <strokeStyle value="solid"/>
        <fillColor value="-1761607681"/>
    </detail>
</event>'''
    
    return cot_xml

async def send_kml_to_tak(kml_file, tak_host="10.212.2.206", tak_port=8089):
    """Convert KML to CoT and send to TAK server"""
    
    print(f"Converting {kml_file} to CoT...")
    cot_messages = parse_kml_to_cot(kml_file)
    
    print(f"Found {len(cot_messages)} objects in KML")
    
    # Certificate paths
    cert_dir = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/"
    client_cert = os.path.join(cert_dir, "user_pytac_mac.pem")
    client_key = os.path.join(cert_dir, "user_pytac_mac.key")
    ca_cert = os.path.join(cert_dir, "ca.pem")
    
    # Create SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_cert_chain(client_cert, client_key, password="atakatak")
    ssl_context.load_verify_locations(ca_cert)
    
    try:
        reader, writer = await asyncio.open_connection(
            tak_host, tak_port, ssl=ssl_context
        )
        
        print(f"Connected to TAK server at {tak_host}:{tak_port}")
        
        for i, cot_xml in enumerate(cot_messages, 1):
            print(f"Sending object {i}/{len(cot_messages)}")
            writer.write(cot_xml.encode('utf-8'))
            await writer.drain()
            await asyncio.sleep(0.5)
        
        print("All KML objects sent to TAK!")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with both KML files
    import sys
    
    if len(sys.argv) > 1:
        kml_file = sys.argv[1]
    else:
        kml_file = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/test_points.kml"
    
    asyncio.run(send_kml_to_tak(kml_file))