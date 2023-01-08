# Modules
from pygnmi.client import gNMIclient
import json


# Variables
host = {
    "ip_address": "192.168.101.17",
    "port": 50051,
    "username": "admin",
    "password": "YourPaSsWoRd",
}


# Body
if __name__ == "__main__":
    with gNMIclient(
        target=(host["ip_address"], host["port"]),
        username=host["username"],
        password=host["password"],
        path_root="certs/ca.pem",
        path_cert="certs/server.pem",
        path_key="certs/server.key",
        override="dev-pygnmi-sonic-003",
        debug=True,
    ) as gc:
        result = gc.capabilities()
        print(json.dumps(result, indent=4))
