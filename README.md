# simple-azure-cni-bash
A simple bash based CNI works to allocate Azure VNET IP and assign to your POD

I got lots of idea from [s-matyukevich](https://github.com/s-matyukevich/bash-cni-plugin/blob/master/01_gcp/bash-cni)， 

## features:
1. to dynamically creates a new ip-config for your Pod, without pre-assigned to VM (Azure VNET CNI is doing this way, but waste a lot of IPs)
   since IP-CONFIG will be created during CNI ADD , this will take much longger time for POD coming up.
   we can not run multiple CNI ADD at same time. so we have to lock and create ip-config one by one,  this even slower when create multiple Pod at same node
2.  assign fixed IP when create new ip-config and assign static IP to a pod (by a annotation, just like calico does.)
3. maybe other....

## how to use:

1. your Azure VM should enable Managed Identify and assign network contributor role to that this identity,
2. make sure jq and azure-cli are installed
3. install this CNI
   - node-ip-alloc:
     ```bash
     wget https://raw.githubusercontent.com/hydracz/simple-azure-cni-bash/main/node-ip-alloc -O /opt/cni/bin/node-ip-alloc
     ```
   - conflist file:  upload to /etc/cni/net.d
   - env file:       upload to /etc/kubernetes:  we might not need this env file later on since we can get all profile from az or using api.
4. to assign static ip to pod, you just need to annotate your pod with following:
   ```yaml
   annotations:
     node-ip-alloc-ipv4-address: 10.0.0.0
     node-ip-alloc-method: static
   ```
