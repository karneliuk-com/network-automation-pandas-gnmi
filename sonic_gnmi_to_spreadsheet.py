# Modules
import os
from pygnmi.client import gNMIclient
import pandas


# Variables
OUTPUT_DIR = "./output"
TARGET = {
    "host": "dev-pygnmi-sonic-003",
    "port": 50051,
    "username": "admin",
    "password": "YourPaSsWoRd",
}


# Body
if __name__ == "__main__":
    with gNMIclient(
        target=(TARGET["host"], TARGET["port"]),
        username=TARGET["username"],
        password=TARGET["password"],
        path_root="certs/ca.pem",
        path_cert="certs/server.pem",
        path_key="certs/server.key",
    ) as gc:
        path = ["/sonic-interface:sonic-interface/INTERFACE"]
        result2 = gc.get(path=path, encoding="json_ietf")

        for path_data in result2["notification"][0]["update"]:
            for path_data_key, path_data_val in path_data["val"].items():
                if not os.path.exists(OUTPUT_DIR):
                    os.mkdir(OUTPUT_DIR)

                spreadsheet = pandas.ExcelWriter(path=f"{OUTPUT_DIR}/{path_data_key}.xlsx")
                sheets = {}

                for entry_key, entry_val in path_data_val.items():
                    target_data = [{"hostname": TARGET["host"], **entry} for entry in entry_val]
                    sheets[entry_key] = pandas.DataFrame(target_data)

                    print(entry_key)
                    print(sheets[entry_key])

                    sheets[entry_key].to_excel(spreadsheet, sheet_name=entry_key)

                spreadsheet.close()
