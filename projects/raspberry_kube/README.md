# Raspberry PI Kubernetes

## Cluster Setup

### Raspberry PI Prep

1. Insert micro SSD card and run raspberry pi imager
2. Select default 64 bit OS and select customise OS
    - Machine name, Set wifi and password auth
3. Insert micro SSD card into raspberry pi 
4. Boot up raspberry bi and attemp to ssh into it using it's local network IP
5. Append "cgroup_memory=1 cgroup_enable=memory" to /boot/firmware/cmdline.txt
6. Run "sudo apt update && sudo apt install iptables"
7. Restart raspberry pi
9. Repeat 1-7. for each node

### K3 installation 

1. Install K3 master node:
    - https://docs.k3s.io/quick-start
    - `curl -sfL https://get.k3s.io | K3S_NODE_NAME=rasp-kube-master sh -`
2. Get master node token with:
    - `sudo cat /var/lib/rancher/k3s/server/node-token`
2. Install worker K3 nodes (for each worker change node name number):
    `curl -sfL https://get.k3s.io | K3S_URL=https://<master-ip>:6443 K3S_TOKEN=<master-node-token> K3S_NODE_NAME=rasp-worker-01 sh -`

Confirm nodes are live on master with:

`kubectrl get nodes`

## Auth

1. Setup ~/.kube/config on master node
2. Copy master node ~/.kube/config -> local machine ~/.kube/config
3. Update host to master node ip
4. Confirm kubectl setup with `kubectrl get nodes`

## Ingress - Inlets

Note: Tried ngrok and removing as cost is too high.

1.

## Cert Manager setup

# To do

1. Document inlet setup 

