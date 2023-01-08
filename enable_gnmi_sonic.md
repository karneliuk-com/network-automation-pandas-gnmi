# gNMI over pyGNMI with Broadcom SONiC

## Documentation
- [Command Reference](https://github.com/sonic-net/sonic-utilities/blob/master/doc/Command-Reference.md)

## Configure SONiC
Welcome to SONiC:
```
sonic login: admin
Password: 
Last login: Fri Apr 22 23:49:11 UTC 2022 on ttyS0
Linux sonic 4.19.0-9-2-amd64 #1 SMP Debian 4.19.118-2+deb10u1 (2020-06-07) x86_64
You are on
  ____   ___  _   _ _  ____
 / ___| / _ \| \ | (_)/ ___|
 \___ \| | | |  \| | | |
  ___) | |_| | |\  | | |___
 |____/ \___/|_| \_|_|\____|

-- Software for Open Networking in the Cloud --

Unauthorized access and/or use are prohibited.
All access and/or use are subject to monitoring.

Help:    http://azure.github.io/SONiC/

admin@sonic:~$
```

### Step 1. Disable ZTP
```
admin@sonic:~$ sudo config ztp disable
---------------------------------------------------------------------------                                                                      
Zero Touch Provisioning discovery in progress. Please disable ZTP or logout.
                                                                               

Active ZTP session will be stopped and disabled, continue? [y/N]: y
Running command: ztp disable -y
```

### Step 2. Change Hostname
```
admin@sonic:~$ sudo config hostname dev-pygnmi-sonic-003
---------------------------------------------------------------------------
Please note loaded setting will be lost after system reboot. To preserve setting, run `config save`.
                                                                               
Broadcast message: Hostname has been changed from 'sonic' to 'dev-pygnmi-sonic-001'. Users running 'sonic-cli' are suggested to restart your session.
```

### Step 3. Configure management IP
```
admin@sonic:~$ sudo config interface ip add eth0 192.168.101.17/24 192.168.101.1
```

### Step 4. Create certificates
At start you will see the telemtry container is failing
```
admin@sonic:~$ sudo docker container ls --all
CONTAINER ID   IMAGE                                COMMAND                  CREATED          STATUS                      PORTS     NAMES
41b1a5310be9   docker-sonic-telemetry:latest        "/usr/local/bin/supe…"   18 minutes ago   Exited (0) 17 minutes ago             telemetry
3000b57f30ea   docker-snmp:latest                   "/usr/local/bin/supe…"   18 minutes ago   Up 18 minutes                         snmp
585372ba71cc   docker-sonic-mgmt-framework:latest   "/usr/local/bin/supe…"   18 minutes ago   Up 18 minutes                         mgmt-framework
a8c0f97cceb0   docker-teamd:latest                  "/usr/local/bin/supe…"   20 minutes ago   Up 20 minutes                         teamd
4983bfb767b7   docker-fpm-frr:latest                "/usr/bin/docker_ini…"   20 minutes ago   Up 20 minutes                         bgp
89f203534a9d   docker-platform-monitor:latest       "/usr/bin/docker_ini…"   20 minutes ago   Up 20 minutes                         pmon
3ca0b5b4eabd   docker-lldp:latest                   "/usr/bin/docker-lld…"   20 minutes ago   Up 20 minutes                         lldp
f92f788f5216   docker-router-advertiser:latest      "/usr/bin/docker-ini…"   21 minutes ago   Up 21 minutes                         radv
f43c0eede468   docker-gbsyncd-vs:latest             "/usr/local/bin/supe…"   21 minutes ago   Up 21 minutes                         gbsyncd
021921df84ea   docker-syncd-vs:latest               "/usr/local/bin/supe…"   21 minutes ago   Up 21 minutes                         syncd
75d604784b18   docker-orchagent:latest              "/usr/bin/docker-ini…"   21 minutes ago   Up 21 minutes                         swss
9dd695cd789b   docker-eventd:latest                 "/usr/local/bin/supe…"   21 minutes ago   Up 21 minutes                         eventd
c605060638c9   docker-database:latest               "/usr/local/bin/dock…"   21 minutes ago   Up 21 minutes                         database
```

However there is no clue there why. The clue is in another file:
```
admin@sonic:~$ sudo cat /var/log/telemetry.log | grep 'no such'
Jan  2 10:34:29.930752 dev-pygnmi-sonic-003 INFO telemetry#supervisord: telemetry F0102 10:34:29.930236      20 telemetry.go:93] could not load server key pair: open /etc/sonic/telemetry/streamingtelemetryserver.cer: no such file or directory
Jan  2 10:35:10.731646 dev-pygnmi-sonic-003 INFO telemetry#supervisord: telemetry F0102 10:35:10.730932      22 telemetry.go:93] could not load server key pair: open /etc/sonic/telemetry/streamingtelemetryserver.cer: no such file or directory
Jan  2 10:35:49.728947 dev-pygnmi-sonic-003 INFO telemetry#supervisord: telemetry F0102 10:35:49.728626      23 telemetry.go:93] could not load server key pair: open /etc/sonic/telemetry/streamingtelemetryserver.cer: no such file or directory
```

Fix:
```
admin@sonic:~$ sudo mkdir -p /etc/sonic/telemetry/
admin@sonic:~$ sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/sonic/telemetry/streamingtelemetryserver.key -out /etc/sonic/telemetry/streamingtelemetryserver.cer -sha256 -days 365 -nodes -subj '/CN=dev-pygnmi-sonic-003'
```

Then restart the container (or reboot the switch generally)

Got another error after:
```
Jan  2 11:04:07.399687 dev-pygnmi-sonic-003 INFO telemetry#supervisord: telemetry F0102 11:04:07.399387      20 telemetry.go:123] could not read CA certificate: open /etc/sonic/telemetry/dsmsroot.cer: no such file or directory
Jan  2 11:04:07.455116 dev-pygnmi-sonic-003 INFO telemetry#supervisord: dialout Yang modles path: /usr/models/yang/
Jan  2 11:04:07.457616 dev-pygnmi-sonic-003 INFO telemetry#supervisord: dialout Yang model List: [sonic-acl.yang sonic-common.yang sonic-extension.yang sonic-extensions.yang sonic-interface.yang sonic-port.yang sonic-show-techsupport.yang sonic-showtech-annot.yang openconfig-acl.yang openconfig-acl-annot.yang]
```

[Some furhter clue](https://github.com/sonic-net/sonic-mgmt/commit/19e92b19c0c7610429402ef15b30288947f6ca13)

```
admin@sonic:~$ sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/sonic/telemetry/dsmsroot.key -out /etc/sonic/telemetry/dsmsroot.cer -sha256 -days 365 -nodes -subj '/CN=lab-ca'
```

#### Proper solution
Generate SS CA certificate and key:
```
admin@sonic:~$ sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/sonic/telemetry/dsmsroot.key \
  -out /etc/sonic/telemetry/dsmsroot.cer -sha256 -days 365 -nodes -subj '/CN=lab-ca'
```

Generate CSR for server:
```
admin@sonic:~$ sudo openssl req -new -newkey rsa:4096 -nodes \
  -keyout /etc/sonic/telemetry/streamingtelemetryserver.key -out /etc/sonic/telemetry/streamingtelemetryserver.csr \
  -subj "/CN=dev-pygnmi-sonic-003"
```

Sign CSR with SS CA:
```
admin@sonic:~$ sudo openssl x509 -req -in /etc/sonic/telemetry/streamingtelemetryserver.csr \
  -CA /etc/sonic/telemetry/dsmsroot.cer -CAkey /etc/sonic/telemetry/dsmsroot.key \
  -CAcreateserial -out /etc/sonic/telemetry/streamingtelemetryserver.cer \
  -days 365 -sha512
```

Restart `telemtry` container:
```
admin@sonic:~$ sudo docker container restart telemetry
telemetry


$ sudo docker container ls
CONTAINER ID   IMAGE                                COMMAND                  CREATED       STATUS         PORTS     NAMES
41b1a5310be9   docker-sonic-telemetry:latest        "/usr/local/bin/supe…"   3 hours ago   Up 9 minutes             telemetry
```

### Step 5. Enable gNMI
Already enabled

### Step 6. Save config
```
admin@sonic:~$ sudo config save
```

### Step 7. Test gNMI
Check what is the port:
```
admin@sonic:~$ ss -tlnp
State   Recv-Q   Send-Q     Local Address:Port      Peer Address:Port  Process  
LISTEN  0        512              0.0.0.0:179            0.0.0.0:*              
LISTEN  0        128              0.0.0.0:22             0.0.0.0:*              
LISTEN  0        3              127.0.0.1:2616           0.0.0.0:*              
LISTEN  0        5              127.0.0.1:3161           0.0.0.0:*              
LISTEN  0        2              127.0.0.1:2620           0.0.0.0:*              
LISTEN  0        100            127.0.0.1:5570           0.0.0.0:*              
LISTEN  0        100            127.0.0.1:5571           0.0.0.0:*              
LISTEN  0        100            127.0.0.1:5572           0.0.0.0:*              
LISTEN  0        100            127.0.0.1:5573           0.0.0.0:*              
LISTEN  0        3              127.0.0.1:2601           0.0.0.0:*              
LISTEN  0        511            127.0.0.1:6379           0.0.0.0:*              
LISTEN  0        3              127.0.0.1:2605           0.0.0.0:*              
LISTEN  0        512                 [::]:179               [::]:*              
LISTEN  0        128                 [::]:22                [::]:*              
LISTEN  0        512                    *:443                  *:*              
LISTEN  0        512                    *:50051                *:*                     <-- This is GNMI port
```
