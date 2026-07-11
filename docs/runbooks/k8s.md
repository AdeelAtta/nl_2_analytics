# Kubernetes Runbook

## View logs
```bash
kubectl logs -n openquery deployment/backend --tail=100
kubectl logs -n openquery deployment/frontend --tail=100
```

## Restart a service
```bash
kubectl rollout restart deployment/backend -n openquery
```

## Scale a service
```bash
kubectl scale deployment/backend --replicas=5 -n openquery
```

## Check pod health
```bash
kubectl get pods -n openquery -o wide
kubectl describe pod -n openquery <pod-name>
```

## Port forward for debugging
```bash
kubectl port-forward -n openquery service/backend 8100:8100
```

## Update image
```bash
kubectl set image deployment/backend backend=ghcr.io/org/upl/backend:latest -n openquery
kubectl rollout status deployment/backend -n openquery
```

## View resource usage
```bash
kubectl top pods -n openquery
kubectl top nodes
```
