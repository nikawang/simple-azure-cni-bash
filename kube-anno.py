from kubernetes import client, config, watch

# 配置 API 客户端
config.load_kube_config()

# 创建 API 实例
v1 = client.CoreV1Api()

# 定义监视函数
def watch_pending_pods_with_annotation(annotation_key):
    w = watch.Watch()
    seen_pods = set()  # 用于跟踪已经看到的 Pod
    for event in w.stream(v1.list_pod_for_all_namespaces):
        pod = event['object']
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace
        pod_key = f"{pod_namespace}/{pod_name}"
        # 检查 Pod 是否处于 Pending 状态并且具有特定的注解
        if pod.status.phase == "Pending":
            annotations = pod.metadata.annotations or {}
            if annotation_key in annotations and pod_key not in seen_pods:
                seen_pods.add(pod_key)  # 将 Pod 添加到已看到的集合中
                print(f"Pod: {pod_name}")
                print(f"Namespace: {pod_namespace}")
                print(f"Annotation {annotation_key}: {annotations[annotation_key]}")
                print("-" * 60)

# 开始监视具有特定注解的 Pending 状态的 Pod
watch_pending_pods_with_annotation('vnet-nic-ipconfig')
