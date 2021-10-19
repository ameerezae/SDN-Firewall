# Firewall Implementation based on SDN
<img src="https://img.shields.io/static/v1?message=Python&logo=python&labelColor=306998&color=ffd43b&logoColor=white&label=%20&style=flat-square" alt="python"> <img src="https://img.shields.io/static/v1?message=OpenFlow&logo=OpenFlow&labelColor=F71735&color=F71735&logoColor=black&label=%20&style=flat-square" alt="pox"> <img src="https://img.shields.io/static/v1?message=POX&logo=pox&labelColor=7E2BF5&color=7E2BF5&logoColor=black&label=%20&style=flat-square" alt="pox"> <img src="https://img.shields.io/static/v1?message=mininet&logo=pox&labelColor=06D6A0&color=06D6A0&logoColor=black&label=%20&style=flat-square" alt="pox">

## Description
**Firewall** Implementation based on Software Defined Networking **(SDN)** using **OpenFlow** controller, In this implementation, I am using  **[POX](https://github.com/noxrepo/pox)** as OpenFlow controller that developed in Python.
## Getting Started
### Dependencies
Dependencies are listed in `requirements.txt` file. \
but i am using `mininet Version2.3.0` which is accessible from [here](https://github.com/mininet/mininet/releases/download/2.3.0/mininet-2.3.0-210211-ubuntu-20.04.1-legacy-server-amd64-ovf.zip).
### Part2 Result
for part2 result of executing commands are shown below:
1. `pingall` command. that host No.1 and host No.4 can ping each other as well as host No.2 and host No.3 .
<img src="./pingall2.png" alt="pingall2">
   

2. `iperf` command. command will hang cause we blocked IP traffic.

<img src="shots/iperf2.png" alt="iperf2">
   

3. `dpctl dump-flows` command. for showing switche flow table rules.

<img src="shots/dpctl2.png" alt="dpctl2">
   
### Part3 Result
for part3 result of executing commands are shown below:
1. `pingall` command. that untrusted host can not ping non of hosts.

<img src="shots/pingall3.png" alt="pingall3">
   

2. `iperf` command. that untrusted host can not send traffic to server and command will hang.

<img src="shots/iperf3.png" alt="iperf3">
   

3. `dpctl dump-flows` command. for showing switches flow table rules.

<img src="shots/dpctl3.png" alt="dpctl3">
   

### Authors
Amir Rezaei [@ameerezae](https://github.com/ameerezae)
