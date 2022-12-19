import time
import pytest
import redis
import logging


@pytest.fixture(scope="function", autouse=True)
def clean(kube):
    # logging.warning("setup")
    yield
    # logging.warning("teardown")
    namespaces = kube.get_namespaces()
    namespace = namespaces[kube.namespace]
    namespace.delete()
    # namespace.wait_until_deleted(60)


@pytest.mark.parametrize("execution_number", range(100))
@pytest.mark.applymanifests("yml", files=["nginx.yaml", "redis.yaml"])
def test_nginx(kube, execution_number):
    """An example test against an Nginx deployment."""
    # wait for the manifests loaded by the 'applymanifests' marker
    # to be ready on the cluster
    kube.wait_for_registered(timeout=30)
    deployments = kube.get_deployments()
    services = kube.get_services()
    nginx_deploy = deployments.get("nginx-deployment")
    assert nginx_deploy is not None
    pods = nginx_deploy.get_pods()
    assert len(pods) == 10, "nginx should deploy with ten replicas"
    for pod in pods:
        containers = pod.get_containers()
        assert len(containers) == 1, "nginx pod should have one container"
        resp = pod.http_proxy_get("/")
        assert "<h1>Welcome to nginx!</h1>" in resp.data

    redis_deploy = services.get("redis-server")

    redis_port = redis_deploy.obj.spec.ports[0].node_port

    r = redis.Redis(host="localhost", port=redis_port, db=0)
    r.set("foo", "bar")
    redis_response = r.get("foo")
    # logging.warning(redis_response)
