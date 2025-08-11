import requests
import urllib3
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import xml.etree.ElementTree as ET
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

class TAKServerRESTClient:
    def __init__(self, tak_host, username, password):
        self.tak_host = tak_host
        self.base_url = f"https://{tak_host}:8446"
        
        self.username = username
        self.password = password
        
        self.session = requests.Session()
        self.session.verify = False
        self._authenticate()
    
    def _authenticate(self):
        # OAuth2 password grant
        oauth_data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }
        
        response = self.session.post(f"{self.base_url}/oauth/token", data=oauth_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            self.session.headers.update({'Authorization': f'Bearer {access_token}'})

    def test_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/Marti/api/database/cotCount")
            print(f"Status code: {response.status_code}")
            if response.status_code == 401:
                print("Authentication failed - check username/password")
            elif response.status_code != 200:
                print(f"Response: {response.text}")
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_cot_direct(self, cot_xml: str) -> bool:
        try:
            # Try sending as raw CoT to the streaming endpoint
            response = self.session.post(
                f"{self.base_url}/Marti/api/cot", 
                data=cot_xml,
                headers={'Content-Type': 'application/xml'}
            )
            print(f"CoT streaming status: {response.status_code}")
            if response.status_code in [200, 201]:
                return True
            
            # If that fails, try the injector endpoint with different payload
            uid = self._extract_uid_from_cot(cot_xml)
            clean_xml = cot_xml.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '').strip()
            
            payload = {
                "uid": uid,
                "toInject": clean_xml
            }
            
            response = self.session.post(f"{self.base_url}/Marti/api/injectors/cot/uid", json=payload)
            print(f"CoT injection status: {response.status_code}")
            if response.status_code not in [200, 201]:
                print(f"Error response: {response.text}")
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"CoT send failed: {e}")
            return False

    def send_cot_via_mission(self, cot_xml: str, mission_name: str = "REST_API_Demo") -> bool:
        try:
            self.create_mission(mission_name)
            mission_content = {
                "data": {
                    "uid": self._extract_uid_from_cot(cot_xml),
                    "submissionTime": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    "keywords": ["REST", "API", "Demo"],
                    "creatorUid": "REST-API-Client",
                    "details": {
                        "cot": cot_xml
                    }
                }
            }
            
            url = f"{self.base_url}/Marti/api/missions/{mission_name}/contents"
            response = self.session.put(url, json=mission_content)
            
            if response.status_code in [200, 201]:
                return True
            else:
                return False
                
        except Exception as e:
            return False

    def create_mission(self, mission_name: str, description: str = "Mission created via REST API") -> bool:
        try:
            url = f"{self.base_url}/Marti/api/missions/{mission_name}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return True
            params = {
                'creatorUid': 'REST-API-Client',
                'description': description,
                'tool': 'REST_API_Demo'
            }
            
            response = self.session.put(url, params=params)
            
            if response.status_code in [200, 201]:
                return True
            else:
                return False
                
        except Exception as e:
            return False

    def send_markers_via_rest(self):
        markers = [
            {
                'uid': f'REST-MARKER-{uuid.uuid4().hex[:8]}',
                'lat': 37.7749, 'lon': -122.4194,
                'callsign': 'REST Unit 1',
                'type': 'a-f-G-U-C',
                'remarks': 'Marker sent via REST API'
            },
            {
                'uid': f'REST-VEHICLE-{uuid.uuid4().hex[:8]}',
                'lat': 37.7849, 'lon': -122.4094,
                'callsign': 'REST Vehicle',
                'type': 'a-f-G-E-V-C',
                'remarks': '🚗 Vehicle marker via REST API'
            },
            {
                'uid': f'REST-EMERGENCY-{uuid.uuid4().hex[:8]}',
                'lat': 37.7649, 'lon': -122.4294,
                'callsign': 'REST Emergency',
                'type': 'b-a-o-tbl',
                'remarks': '🚨 Emergency alert via REST API'
            }
        ]
        
        for marker in markers:
            cot_xml = self._create_marker_cot_xml(marker)
            success = self.send_cot_direct(cot_xml)
            print(f"Marker {marker['callsign']}: {'✅' if success else '❌'}")
            time.sleep(1)

    def send_polygons_via_rest(self):
        polygons = [
            {
                'uid': f'REST-POLYGON-{uuid.uuid4().hex[:8]}',
                'callsign': 'REST Area 1',
                'type': 'u-d-f',
                'remarks': '🔺 Polygon area sent via REST API',
                'coordinates': [
                    [37.7700, -122.4400],
                    [37.7800, -122.4400],
                    [37.7800, -122.4300],
                    [37.7700, -122.4300],
                    [37.7700, -122.4400]
                ]
            },
            {
                'uid': f'REST-CIRCLE-{uuid.uuid4().hex[:8]}',
                'callsign': 'REST Perimeter',
                'type': 'u-d-f',
                'remarks': '🔴 Circular perimeter via REST API',
                'coordinates': self._generate_circle_coordinates(37.7750, -122.4250, 0.005)  # ~500m radius
            }
        ]
        
        for polygon in polygons:
            cot_xml = self._create_polygon_cot_xml(polygon)
            success = self.send_cot_via_mission(cot_xml)
            time.sleep(1)

    def manage_missions_via_rest(self):
        missions = [
            {"name": "REST_Demo_Alpha", "description": "Alpha mission via REST API"},
            {"name": "REST_Demo_Bravo", "description": "Bravo mission via REST API"},
            {"name": "REST_Demo_Charlie", "description": "Charlie mission via REST API"}
        ]
        
        for mission in missions:
            self.create_mission(mission["name"], mission["description"])
            time.sleep(0.5)
        self.list_missions()
        for i, mission in enumerate(missions):
            marker = {
                'uid': f'MISSION-MARKER-{i+1}',
                'lat': 37.7749 + (i * 0.01), 
                'lon': -122.4194 + (i * 0.01),
                'callsign': f'Mission {mission["name"]} HQ',
                'type': 'a-f-G-I-U-T-com',
                'remarks': f'🎯 Headquarters for {mission["name"]}'
            }
            
            cot_xml = self._create_marker_cot_xml(marker)
            self.send_cot_via_mission(cot_xml, mission["name"])
            time.sleep(0.5)

    def list_missions(self):
        try:
            url = f"{self.base_url}/Marti/api/missions"
            response = self.session.get(url)
            
            if response.status_code == 200:
                missions_data = response.json()
                if 'data' in missions_data:
                    missions = missions_data['data']
                    for mission in missions:
                        print(f"  - {mission.get('name', 'Unknown')}: {mission.get('description', 'No description')}")
            else:
                raise Exception(f"Failed to list missions - Status: {response.status_code}")
                
        except Exception as e:
            raise e

    def send_data_package_via_rest(self):
        try:
            file_content = f"""TAK Server REST API Demo
Generated at: {datetime.now()}
This is a test data package sent via REST API.

Mission Report:
- Status: Operational
- Location: San Francisco Bay Area
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            files = {
                'assetfile': ('demo_report.txt', file_content, 'text/plain')
            }
            
            url = f"{self.base_url}/Marti/sync/upload"
            response = self.session.post(url, files=files)
            
            if response.status_code in [200, 201]:
                print(f"Data package uploaded successfully {response.text}")
            else:
                raise Exception(f"Failed to upload data package - Status: {response.status_code}")
                
        except Exception as e:
            raise e

    def get_server_info_via_rest(self):
        endpoints_to_check = [
            ("/Marti/api/version", "Server Version"),
            ("/Marti/api/version/info", "Version Info"),
            ("/Marti/api/version/config", "Server Config"),
            ("/Marti/api/subscriptions/all", "Active Subscriptions")
        ]
        
        for endpoint, description in endpoints_to_check:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    if endpoint == "/Marti/api/version":
                        print(f"   Version: {response.text}")
                    elif "subscriptions" in endpoint:
                        try:
                            data = response.json()
                            if 'data' in data:
                                count = len(data['data'])
                                print(f"   Active connections: {count}")
                        except:
                            print(f"   Raw response length: {len(response.text)} chars")
                else:
                    print(f"⚠️ {description}: Status {response.status_code}")
                    
            except Exception as e:
                raise e
            
            time.sleep(0.5)

    def _create_marker_cot_xml(self, marker: Dict[str, Any]) -> str:
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
        <color argb="-1"/>
    </detail>
</event>'''

    def _create_polygon_cot_xml(self, polygon: Dict[str, Any]) -> str:
        now = datetime.now(timezone.utc)
        time_str = now.isoformat().replace('+00:00', 'Z')
        stale_time = datetime.fromtimestamp(now.timestamp() + 300, timezone.utc)
        stale_str = stale_time.isoformat().replace('+00:00', 'Z')
        
        coords = polygon['coordinates']
        center_lat = sum(coord[0] for coord in coords) / len(coords)
        center_lon = sum(coord[1] for coord in coords) / len(coords)
        
        polygon_points = ""
        for coord in coords:
            polygon_points += f'            <vertex lat="{coord[0]}" lon="{coord[1]}" hae="0"/>\n'
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{polygon['uid']}" type="{polygon['type']}" time="{time_str}" start="{time_str}" stale="{stale_str}" how="h-g-i-g-o">
    <point lat="{center_lat}" lon="{center_lon}" hae="0" ce="10" le="10"/>
    <detail>
        <contact callsign="{polygon['callsign']}" endpoint="*:-1:stcp"/>
        <remarks>{polygon['remarks']}</remarks>
        <link_attr color="-65536" type="b-m-p-s-m" style="0"/>
        <shape>
            <polygon>
{polygon_points.rstrip()}
            </polygon>
        </shape>
        <precisionlocation geopointsrc="GPS" altsrc="GPS"/>
        <archive/>
    </detail>
</event>'''

    def _generate_circle_coordinates(self, center_lat: float, center_lon: float, radius: float, points: int = 16) -> List[List[float]]:
        import math
        
        coordinates = []
        for i in range(points + 1):
            angle = 2 * math.pi * i / points
            lat = center_lat + radius * math.cos(angle)
            lon = center_lon + radius * math.sin(angle)
            coordinates.append([lat, lon])
        
        return coordinates

    def _extract_uid_from_cot(self, cot_xml: str) -> str:
        try:
            root = ET.fromstring(cot_xml)
            return root.get('uid', f'UNKNOWN-{uuid.uuid4().hex[:8]}')
        except:
            return f'UNKNOWN-{uuid.uuid4().hex[:8]}'

def main():
    client = TAKServerRESTClient(tak_host="10.212.2.206", username="newadmin", password="MyPassword12345!")
    if not client.test_connection():
        print("Cannot connect to TAK server. Please check:")
        return
    
    try:
        client.get_server_info_via_rest()
        client.send_markers_via_rest()
        client.send_polygons_via_rest()
        client.manage_missions_via_rest()
        client.send_data_package_via_rest()
        
    except Exception as e:
        raise e
        
    finally:
        client.session.close()

if __name__ == "__main__":
    main()