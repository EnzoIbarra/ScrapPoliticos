import requests
import os
import time
from src.worker import get_proxy

def test_tor():
    proxies = get_proxy()
    print(f"Usando proxies: {proxies}")
    
    # Tor puede tardar en establecer el circuito
    for i in range(5):
        try:
            print(f"Intento {i+1}/5 de conexión...")
            response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=30)
            ip_anonima = response.json()['ip']
            print(f"IP Tor detectada: {ip_anonima}")
            return True
        except Exception as e:
            print(f"Esperando a Tor... ({e})")
            time.sleep(10)
    return False

if __name__ == "__main__":
    test_tor()
