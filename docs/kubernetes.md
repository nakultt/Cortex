# Kubernetes Local Deployment

## Quick Start

```powershell
# 1. Start Minikube
minikube start

# 2. Build images
docker build -t cortex-backend:local ./backend
docker build -t cortex-frontend:local ./frontend

# 3. Load images into Minikube
minikube image load cortex-backend:local
minikube image load cortex-frontend:local

# 4. Deploy
kubectl apply -k k8s/

# 5. Port-forward services (run each in a separate terminal)
kubectl port-forward -n cortex svc/cortex-frontend 3000:80
kubectl port-forward -n cortex svc/cortex-backend 8000:8000
kubectl port-forward -n cortex svc/cortex-neo4j 7474:7474
kubectl port-forward -n cortex svc/cortex-qdrant 6333:6333
kubectl port-forward -n cortex svc/cortex-postgres 5432:5432
```

## Access URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Neo4j Browser | http://localhost:7474 |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| PostgreSQL | localhost:5432 (use pgAdmin/DBeaver) |

## Useful Commands

```powershell
# View pods
kubectl get pods -n cortex

# View logs
kubectl logs -n cortex deployment/cortex-backend -f

# Restart deployments
kubectl rollout restart deployment -n cortex

# Delete everything
kubectl delete namespace cortex

# Stop Minikube
minikube stop
```
