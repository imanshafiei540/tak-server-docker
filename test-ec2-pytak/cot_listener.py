import asyncio
import ssl
import os
from datetime import datetime

async def listen_for_cot():
    cert_dir = "/Users/iman.shafiei/Workspace/EDA/tak-server-docker/test-ec2-pytak/certs/"
    client_cert = os.path.join(cert_dir, "user_pytac_mac.pem")
    client_key = os.path.join(cert_dir, "user_pytac_mac.key")
    ca_cert = os.path.join(cert_dir, "ca.pem")
    
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_cert_chain(client_cert, client_key, password="atakatak")
    ssl_context.load_verify_locations(ca_cert)
    
    try:
        reader, writer = await asyncio.open_connection(
            "10.212.2.206", 8089, ssl=ssl_context
        )
        print("Connected to TAK server - listening for messages...")
        
        while True:
            data = await reader.read(4096)
            if not data:
                break
                
            try:
                xml_data = data.decode('utf-8')
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if xml_data.strip().startswith('<?xml') or xml_data.strip().startswith('<event'):
                    print(f"\n[{timestamp}] Received CoT XML:")
                    print("-" * 40)
                    print(xml_data)
                    print("-" * 40)
                    
            except UnicodeDecodeError:
                pass
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'writer' in locals():
            writer.close()

if __name__ == "__main__":
    asyncio.run(listen_for_cot())