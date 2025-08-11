import asyncio
import pytak
import random
import time
from datetime import datetime, timezone
import uuid
import logging
import xml.etree.ElementTree as ET
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedTAKSerializer(pytak.QueueWorker):
    def __init__(self, queue, config):
        super().__init__(queue, config)
        self.tak_host = config.get('TAK_HOST', '10.212.2.206')
        self.tak_port = int(config.get('TAK_PORT', '8089'))
        self.my_uid = f"PYTAK-ADV-{uuid.uuid4().hex[:8]}"
        self.sent_static = False

    async def handle_data(self, data):
        """Handle data and put CoT events on queue"""
        await self.put_queue(data)

    async def run(self, number_of_iterations=-1):
        """Main run loop"""
        if not self.sent_static:
            await self._send_unit_markers()
            await self._send_complex_polygons()
            await self._send_mission_objects()
            await self._send_emergency_alerts()
            await self._send_chat_message()
            self.sent_static = True
            
        await self._simulate_moving_unit()

    async def _send_unit_markers(self):
        unit_markers = [
            {
                'uid': f'UNIT-INF-{uuid.uuid4().hex[:8]}',
                'lat': 37.7749, 'lon': -122.4194,
                'callsign': 'Alpha Squad',
                'type': 'a-f-G-U-C-I',
                'remarks': 'Infantry squad - 8 personnel'
            },
            {
                'uid': f'UNIT-ARM-{uuid.uuid4().hex[:8]}',
                'lat': 37.7849, 'lon': -122.4094,
                'callsign': 'Tank-01',
                'type': 'a-f-G-E-V-T',
                'remarks': 'M1A2 Abrams Main Battle Tank'
            },
            {
                'uid': f'UNIT-AIR-{uuid.uuid4().hex[:8]}',
                'lat': 37.7949, 'lon': -122.3994,
                'callsign': 'Eagle-1',
                'type': 'a-f-A-M-F-Q',
                'remarks': 'F/A-18 Super Hornet on patrol',
                'hae': 15000
            },
            {
                'uid': f'UNIT-MED-{uuid.uuid4().hex[:8]}',
                'lat': 37.7649, 'lon': -122.4294,
                'callsign': 'Medic-1',
                'type': 'a-f-G-E-V-m',
                'remarks': 'Mobile medical unit - CASEVAC ready'
            },
            {
                'uid': f'UNIT-CMD-{uuid.uuid4().hex[:8]}',
                'lat': 37.7549, 'lon': -122.4394,
                'callsign': 'Command-1',
                'type': 'a-f-G-I-U-T-com',
                'remarks': 'Tactical Operations Center'
            }
        ]
        
        for marker in unit_markers:
            cot_xml = self._create_cot_xml(marker)
            await self.handle_data(cot_xml)
            await asyncio.sleep(0.5)

    async def _send_complex_polygons(self):
        area_corners = [
            {
                'uid': f'CORNER-1-{uuid.uuid4().hex[:8]}',
                'lat': 37.7600, 'lon': -122.4500,
                'callsign': 'AO-Corner-1',
                'type': 'b-m-p-w',
                'remarks': 'AO Phoenix - Southwest corner'
            },
            {
                'uid': f'CORNER-2-{uuid.uuid4().hex[:8]}',
                'lat': 37.7900, 'lon': -122.4500,
                'callsign': 'AO-Corner-2',
                'type': 'b-m-p-w',
                'remarks': 'AO Phoenix - Northwest corner'
            },
            {
                'uid': f'CORNER-3-{uuid.uuid4().hex[:8]}',
                'lat': 37.7900, 'lon': -122.4000,
                'callsign': 'AO-Corner-3',
                'type': 'b-m-p-w',
                'remarks': 'AO Phoenix - Northeast corner'
            },
            {
                'uid': f'CORNER-4-{uuid.uuid4().hex[:8]}',
                'lat': 37.7600, 'lon': -122.4000,
                'callsign': 'AO-Corner-4',
                'type': 'b-m-p-w',
                'remarks': 'AO Phoenix - Southeast corner'
            }
        ]
        
        for corner in area_corners:
            cot_xml = self._create_cot_xml(corner)
            await self.handle_data(cot_xml)
            await asyncio.sleep(0.5)

    async def _send_mission_objects(self):
        route_waypoints = [
            {
                'uid': f'ROUTE-START-{uuid.uuid4().hex[:8]}',
                'lat': 37.7749, 'lon': -122.4194,
                'callsign': 'Route-Start',
                'type': 'b-m-p-w',
                'remarks': 'Route start point'
            },
            {
                'uid': f'ROUTE-WP1-{uuid.uuid4().hex[:8]}',
                'lat': 37.7800, 'lon': -122.4150,
                'callsign': 'Route-WP1',
                'type': 'b-m-p-w',
                'remarks': 'Route waypoint 1'
            },
            {
                'uid': f'ROUTE-WP2-{uuid.uuid4().hex[:8]}',
                'lat': 37.7850, 'lon': -122.4100,
                'callsign': 'Route-WP2',
                'type': 'b-m-p-w',
                'remarks': 'Route waypoint 2'
            },
            {
                'uid': f'ROUTE-WP3-{uuid.uuid4().hex[:8]}',
                'lat': 37.7900, 'lon': -122.4050,
                'callsign': 'Route-WP3',
                'type': 'b-m-p-w',
                'remarks': 'Route waypoint 3'
            },
            {
                'uid': f'ROUTE-END-{uuid.uuid4().hex[:8]}',
                'lat': 37.7950, 'lon': -122.4000,
                'callsign': 'Route-End',
                'type': 'b-m-p-w',
                'remarks': 'Route end point'
            }
        ]
        
        for waypoint in route_waypoints:
            cot_xml = self._create_cot_xml(waypoint)
            await self.handle_data(cot_xml)
            await asyncio.sleep(0.5)

    async def _send_emergency_alerts(self):
        alert = {
            'uid': f'ALERT-{uuid.uuid4().hex[:8]}',
            'lat': 37.7750, 'lon': -122.4250,
            'callsign': 'EMERGENCY',
            'type': 'b-a-o-tbl',
            'remarks': 'URGENT: Troops in contact - immediate support needed!'
        }
        
        cot_xml = self._create_cot_xml(alert)
        await self.handle_data(cot_xml)
        await asyncio.sleep(1)

    async def _send_chat_message(self):
        chat_msg = {
            'uid': f'CHAT-{uuid.uuid4().hex[:8]}',
            'lat': 37.7750, 'lon': -122.4250,
            'callsign': 'PyTAK-Bot',
            'type': 'b-t-f',
            'remarks': 'Hello from PyTAK! This is an automated message from the comprehensive example script.'
        }
        
        cot_xml = self._create_cot_xml(chat_msg)
        await self.handle_data(cot_xml)

    async def _simulate_moving_unit(self):
        start_lat, start_lon = 37.7694, -122.4862
        uid = f'UNIT-PATROL-{uuid.uuid4().hex[:8]}'
        update_count = 0
        
        while True:
            lat_offset = random.uniform(-0.001, 0.001)
            lon_offset = random.uniform(-0.001, 0.001)
            
            current_lat = start_lat + lat_offset
            current_lon = start_lon + lon_offset
            
            unit_data = {
                'uid': uid,
                'lat': current_lat,
                'lon': current_lon,
                'callsign': 'Patrol-Alpha',
                'type': 'a-f-G-U-C',
                'remarks': f'Mobile patrol unit - Update #{update_count + 1}'
            }
            
            cot_xml = self._create_cot_xml(unit_data)
            await self.handle_data(cot_xml)
            
            update_count += 1
            await asyncio.sleep(10)

    def _create_cot_xml(self, data):
        now = datetime.now(timezone.utc)
        time_str = now.isoformat().replace('+00:00', 'Z')
        stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
        stale_str = stale_time.isoformat().replace('+00:00', 'Z')
        
        root = ET.Element("event")
        root.set("version", "2.0")
        root.set("uid", data['uid'])
        root.set("type", data['type'])
        root.set("time", time_str)
        root.set("start", time_str)
        root.set("stale", stale_str)
        root.set("how", "h-g-i-g-o")
        
        point = ET.SubElement(root, "point")
        point.set("lat", str(data['lat']))
        point.set("lon", str(data['lon']))
        point.set("hae", str(data.get('hae', 0.0)))
        point.set("ce", "10")
        point.set("le", "10")
        
        detail = ET.SubElement(root, "detail")
        contact = ET.SubElement(detail, "contact")
        contact.set("callsign", data['callsign'])
        contact.set("endpoint", "*:-1:stcp")
        
        remarks = ET.SubElement(detail, "remarks")
        remarks.text = data['remarks']
        
        precision = ET.SubElement(detail, "precisionlocation")
        precision.set("geopointsrc", "GPS")
        precision.set("altsrc", "GPS")
        
        color = ET.SubElement(detail, "color")
        color.set("argb", "-1")
        
        return ET.tostring(root, encoding='utf-8')

    def _create_polygon_cot_xml(self, polygon_data):
        now = datetime.now(timezone.utc)
        time_str = now.isoformat().replace('+00:00', 'Z')
        stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
        stale_str = stale_time.isoformat().replace('+00:00', 'Z')

        coords = polygon_data['coordinates']
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        center_lat = sum(coord[0] for coord in coords) / len(coords)
        center_lon = sum(coord[1] for coord in coords) / len(coords)

        root = ET.Element("event")
        root.set("version", "2.0")
        root.set("uid", polygon_data['uid'])
        root.set("type", polygon_data.get('type', 'u-d-f'))
        root.set("time", time_str)
        root.set("start", time_str)
        root.set("stale", stale_str)
        root.set("how", "h-g-i-g-o")

        point = ET.SubElement(root, "point")
        point.set("lat", str(center_lat))
        point.set("lon", str(center_lon))
        point.set("hae", "0.0")
        point.set("ce", "9999999.0")
        point.set("le", "9999999.0")

        detail = ET.SubElement(root, "detail")
        shape = ET.SubElement(detail, "shape")
        polyline = ET.SubElement(shape, "polyline")
        polyline.set("closed", "true")

        for coord in coords:
            vertex = ET.SubElement(polyline, "vertex")
            vertex.set("lat", str(coord[0]))
            vertex.set("lon", str(coord[1]))
            vertex.set("hae", "0.0")

        contact = ET.SubElement(detail, "contact")
        contact.set("callsign", polygon_data.get('callsign', 'Polygon'))

        remarks = ET.SubElement(detail, "remarks")
        remarks.text = polygon_data.get('remarks', 'Polygon Area')

        return ET.tostring(root, encoding='utf-8')

async def main():
    config = ConfigParser()
    config["takexample"] = {
        "COT_URL": "tls://10.212.2.206:8089",
        "PYTAK_TLS_CLIENT_CERT": "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/user_pytac_mac.pem",
        "PYTAK_TLS_CLIENT_KEY": "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/user_pytac_mac.key",
        "PYTAK_TLS_CLIENT_PASSWORD": "atakatak",
        "PYTAK_TLS_DONT_VERIFY": "true",
        "PYTAK_TLS_DONT_CHECK_HOSTNAME": "true",
        "TAK_HOST": "10.212.2.206",
        "TAK_PORT": "8089"
    }
    config = config["takexample"]
    
    try:
        clitool = pytak.CLITool(config)
        await clitool.setup()
        clitool.add_tasks(set([AdvancedTAKSerializer(clitool.tx_queue, config)]))
        await clitool.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())