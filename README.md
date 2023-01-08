# Network Automation and Data Analysis
This repo contains various Python script and testing documentation explaining how to automate and analyze data in networking. As a basis we took Microsoft Azure SONiC, which is one of the most quickly developing networking platforms for high- and hyper- scale data centres. In such settings the proper management can be achieved only via automation and programmability. The good news is that SONiC supports a great protocol for such a purpose - GNMI, which gives you possibility to do collection of network data or perform configuration in a transactional mode as well as to collect the streaming and event-based telemetry data.

## Prepare SONiC to work with GNMI
1. [Get latest stables SONiC](https://sonic-net.github.io/SONiC/sonic_latest_images.html)
2. Follow the steps to [configure GNMI provided in this guide](https://bit.ly/3IiArXD)

## How to use this repository
1. Clone it to your host.
2. Install the content of `requirements.txt` for your Python.
3. Ensure you followed steps above, create certificates and copied them to local directory `certs`.
4. Amend the credentials in the python files.
5. Run the `python sonic_test.py` or `sonic_gnmi_to_spreadsheet.py`.
