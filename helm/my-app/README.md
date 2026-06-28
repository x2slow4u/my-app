# Helm Chart

Helm chart для запуска приложения в Kubernetes.

## Что Входит

- Flask app Deployment с readiness/liveness probes.
- PostgreSQL Deployment, Service и PVC.
- Redis Deployment, Service и PVC.
- ClusterIP Service для приложения.
- HPA для web Deployment.
- Опциональный Ingress.

## Установка

```bash
helm upgrade --install my-app ./helm/my-app \
  --namespace my-app \
  --create-namespace
```

Если GHCR image private, сначала создай pull secret:

```bash
kubectl create secret docker-registry ghcr-auth \
  --namespace my-app \
  --docker-server=ghcr.io \
  --docker-username=<github-username> \
  --docker-password=<github-token>
```

И передай его chart:

```bash
helm upgrade --install my-app ./helm/my-app \
  --namespace my-app \
  --create-namespace \
  --set imagePullSecrets[0].name=ghcr-auth
```

Проверка:

```bash
kubectl get pods -n my-app
kubectl get hpa -n my-app
kubectl port-forward -n my-app svc/my-app-my-app-web 8080:80
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

## Rollback Demo

Посмотреть revisions:

```bash
helm history my-app -n my-app
```

Откатиться на предыдущую revision:

```bash
helm rollback my-app 1 -n my-app
```

## Удаление

```bash
helm uninstall my-app -n my-app
```
