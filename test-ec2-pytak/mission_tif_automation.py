import requests
import urllib3
import os
import sys
import random
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upload_tif_to_mission(tif_path, mission_name=None):
    """Simple function that follows your exact curl commands"""
    
    if not os.path.exists(tif_path):
        print(f"File not found: {tif_path}")
        return False
    
    if not mission_name:
        random_num = random.randint(1000, 9999)
        mission_name = f"TestMission{random_num}"
    
    session = requests.Session()
    session.verify = False
    
    print("Getting OAuth token...")
    oauth_data = {
        'grant_type': 'password',
        'username': 'newadmin',
        'password': 'MyPassword12345!'
    }
    
    response = session.post("https://10.212.2.206:8446/oauth/token", data=oauth_data)
    if response.status_code != 200:
        print(f"Auth failed: {response.status_code}")
        return False
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://10.212.2.206:8443/Marti/MissionManager.html',
        'Origin': 'https://10.212.2.206:8443',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'Priority': 'u=0',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }
    session.headers.update(headers)
    
    print(f"Processing: {os.path.basename(tif_path)} -> {mission_name}")
    
    encoded_name = quote(mission_name)
    url = f"https://10.212.2.206:8446/Marti/api/missions/{encoded_name}"
    params = {
        'description': 'Description',
        'group': '__ANON__',
        'allowGroupChange': 'true',
        'tool': 'REST_API_Demo',
        'defaultRole': '',
        'expiration': '-1'
    }
    
    response = session.put(url, params=params, headers={'Content-Length': '0'})
    if response.status_code in [200, 201, 409]:
        print(f"Step 1 - Mission: {response.status_code}")
    else:
        print(f"Step 1 failed: {response.status_code}")
        return False
    
    keywords_url = f"https://10.212.2.206:8446/Marti/api/missions/{encoded_name}/keywords"
    response = session.put(keywords_url, json=[], headers={'Content-Type': 'application/json'})
    if response.status_code in [200, 201]:
        print(f"Step 2 - Keywords: {response.status_code}")
    else:
        print(f"Step 2 failed: {response.status_code}")
    
    filename = os.path.basename(tif_path)
    with open(tif_path, 'rb') as f:
        files = {'assetfile': (filename, f, 'image/tiff')}
        response = session.post('https://10.212.2.206:8446/Marti/sync/upload', files=files)
    
    if response.status_code not in [200, 201]:
        print(f"Step 3 - Upload failed: {response.status_code}")
        return False
    
    print(f"Step 3 - Upload: {response.status_code}")
    
    try:
        upload_response = response.json()
        file_hash = upload_response.get('Hash', upload_response.get('hash', 'unknown'))
        print(f"File hash: {file_hash}")
    except:
        print("Could not extract file hash, using placeholder")
        file_hash = "3aeb1007931499ae5f3688fb997bbde39db0cc659c807a26d6cf6309b929ecbc"
    
    contents_url = f"https://10.212.2.206:8446/Marti/api/missions/{encoded_name}/contents"
    payload = {"hashes": [file_hash]}
    params = {'creatorUid': 'admin'}
    
    response = session.put(contents_url, json=payload, params=params, headers={'Content-Type': 'application/json'})
    if response.status_code in [200, 201]:
        print(f"Step 4 - Add to mission: {response.status_code}")
        print(f"Done! Check: https://10.212.2.206:8446/Marti/MissionManager.html")
        return True
    else:
        print(f"Step 4 failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    # tif_path = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/CBERS_4_MUX_20230928_065_102_L2_BAND5.tif"
    # tif_path = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/map.kml"
    # tif_path = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/11214@2x.tiff"
    # tif_path = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/11214@2x.mbtiles"
    tif_path = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/Canada.kmz"
    
    if not os.path.exists(tif_path):
        print(f"Change the hardcoded path in the script to your file")
        sys.exit(1)
    
    upload_tif_to_mission(tif_path)
