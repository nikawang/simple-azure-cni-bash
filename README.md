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
2. make sure jq / kubelet / azure-cli are installed
   - jq:
     ```bash
     yum install -y epel-release
     yum install -y jq
     ```
   - azure-cli:
     [azure-cli-installation](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=dnf)，
   
3. install this CNI
   - node-ip-alloc:
     ```bash
     wget https://raw.githubusercontent.com/hydracz/simple-azure-cni-bash/main/node-ip-alloc -O /opt/cni/bin/node-ip-alloc
     ```

    - conflist file:  upload to /etc/cni/net.d
     ```
      wget https://raw.githubusercontent.com/hydracz/simple-azure-cni-bash/main/09-cni.conflist -O /etc/cni/net.d/10-azure.conflist
     ```

     ```json
      {
        "cniVersion":"0.3.0",
        "name":"azure",
        "plugins":[
          {
            "type": "node-ip-alloc",
            "kubeletconf":"/etc/kubernetes/kubelet.conf"
          }
        ]
      }
      ```
   - prepare env file:  upload to /etc/kubernetes/centos-k8s-cluster.env: currently 3 madatory ENV has to be present for this CNI to allocate ip-config and ips.  different node will have different settings.  I'm currently using a terraform per node template to generate this env..
  
      ```json
      # cat /etc/kubernetes/centos-k8s-cluster.env
      export NODE_NIC_NAME="k8s-master-0-nic"
      export NODE_SUBNET_CIDR="10.0.0.0/17"
      export NODE_RG_NAME="rg-centos-k8s-southeastasia"
      ```

4. to assign static ip to pod, you just need to annotate your pod with following:
   ```yaml
   annotations:
     node-ip-alloc-ipv4-address: 10.0.0.0
     node-ip-alloc-method: static
   ```
