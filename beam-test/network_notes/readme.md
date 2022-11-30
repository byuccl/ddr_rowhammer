1. Run command to see Ethernet connections: `ip link show` to find the network name and the mac address:

```
shrec@nuc4:~/ddr/ddr_mjw/ddr_rowhammer/beam-test/test_scripts$ ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether f4:4d:30:65:51:ac brd ff:ff:ff:ff:ff:ff
    altname enp0s31f6
3: wlp1s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DORMANT group default qlen 1000
    link/ether 00:c2:c6:f3:24:15 brd ff:ff:ff:ff:ff:ff
4: enxa0cec803ae9e: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether a0:ce:c8:03:ae:9e brd ff:ff:ff:ff:ff:ff
6: enxa0cec8082364: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN mode DEFAULT group default qlen 1000
    link/ether a0:ce:c8:08:23:64 brd ff:ff:ff:ff:ff:ff
```

In this case, the dongle is the `enxa0cec8082364`. 

2. Link the adapter to fpga0

`sudo ip link property add dev enxa0cec8082364 altname fpga0`

3. Check to see if it is successfully linked:

`ip addr show dev fpga0`

4. Edit `/etc/netplan/01-network-manager-all.yaml` as described below:

`sudoedit /etc/netplan/01-network-manager-all.yaml`

Example of netplan document with network with altname fpga0:

```
# Let NetworkManager manage all devices on this system
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    fpga0:
      dhcp4: no
      addresses:
        - 192.168.100.2/24
```

5. Apply the changes and see if they worked

```
sudo netplan apply
ip link show
```
6. Get the link to be up

`sudo ip link set fpga0 up`
`ip link show`

sudo ip addr add 192.168.100.2/24 dev <name>

ip link show








More commands:

litex_server --udp --udp-ip 192.168.100.50 --udp-port 1234
