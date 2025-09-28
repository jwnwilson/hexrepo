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

1 Setup digital ocean and follow these docs:
https://docs.inlets.dev/tutorial/kubernetes-ingress/#install-the-inlets-operator


## Cert Manager setup

# To do

1. Document inlet setup 

## ECR auth setup
export USERNAME=noelwilson
export IP=192.168.1.49
scp ./ecr-credential-provider $USERNAME@$IP:/tmp
ssh $USERNAME@$IP "chmod +x /tmp/ecr-credential-provider"
ssh $USERNAME@$IP "mv /tmp/ecr-credential-provider /var/lib/rancher/credentialprovider/bin/ecr-credential-provider" 
kubectl apply -f ./infra/credential-provider-config.yaml


## ECR setup

Setup cron job to refresh docker access token for aws ecr.
Guide here: https://cjihrig.com/refreshing_k8s_docker_secrets_via_cron

Private ECR setup:
1.Gave admin permissions to default service account
```
kubectl create clusterrolebinding permissive-binding \
  --clusterrole=cluster-admin \
  --user=admin \
  --user=kubelet \
  --group=system:serviceaccounts
```
2. Setup aws auth, run: add_aws_ecr_creds.sh
3. Setup ECR auth, run: docker_auth.sh


clusterrolebinding.rbac.authorization.k8s.io/permissive-binding created




