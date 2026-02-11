#  Containerised Uptime Stack on Kubernetes (with Local CI/CD)

A **fully containerised uptime-monitoring application** deployed on Kubernetes with GitOps-style configuration, observability patterns, and a local CI/CD workflow.

This project demonstrates end-to-end DevOps fundamentals: containerisation, Kubernetes orchestration, access control, networking policies, workload scaling, persistent storage, configuration management, and automated deployment.

---

##  Features

| Capability                   | Implementation                                       |
| ---------------------------- | ---------------------------------------------------- |
| **Application**              | Flask-based uptime service                           |
| **Containerisation**         | Docker image with lightweight runtime                |
| **Orchestration**            | Kubernetes Deployment + Service + Ingress            |
| **Namespace Isolation**      | Dedicated `uptime-dev` namespace                     |
| **Access Control**           | RBAC with scoped ServiceAccount for CronJob          |
| **Networking Security**      | Kubernetes NetworkPolicy                             |
| **Scheduled Jobs**           | Kubernetes CronJob for periodic health checks        |
| **Persistence**              | PostgreSQL via StatefulSet                           |
| **Auto-Scaling**             | Horizontal Pod Autoscaler (HPA) using Metrics Server |
| **Configuration Management** | **Kustomize**                                        |
| **CI/CD (Local)**            | Jenkins pipeline for build → push → deploy           |

---

##  Architecture Overview

```
Flask App
   │
Docker Image ──▶ Local Registry (localhost:5001)
   │
Jenkins Pipeline ──▶ kubectl apply -k kustomize
   │
Kubernetes Cluster
   ├── Deployment (uptime-app)
   ├── Service (ClusterIP)
   ├── Ingress (nginx)
   ├── CronJob (health checks)
   ├── StatefulSet (Postgres)
   ├── HPA (CPU-based scaling)
   ├── RBAC (least-privilege access)
   └── NetworkPolicy (pod-level security)
```

---

##  Repository Structure

```
Containerised-Uptime-Stack-on-Kubernetes-with-Local-CI-CD/
│
├── app/                 # Flask application + Dockerfile
├── kustomize/           # Kubernetes manifests managed via Kustomize
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── kustomization.yml
│
├── k8s/
│   ├── namespace.yaml
│   ├── HPA/
│   ├── db/              # Postgres StatefulSet & Service
│   └── rbac/            # Role + RoleBinding
│
├── jobs/                # CronJob manifests
├── registry/            # Local Docker registry (docker compose)
├── ci/
│   └── Jenkinsfile      # CI/CD pipeline definition
└── README.md            # You are reading it 😊
```

---

##  Prerequisites

You need:

* Docker Desktop
* Kubernetes (Docker Desktop Kubernetes or Minikube)
* kubectl
* metrics-server installed
* Jenkins (local)
* Local Docker registry running on `localhost:5001`

Start registry:

```bash
cd registry
docker compose up -d
```

---

##  Deploying with Kustomize

Apply all core manifests using:

```bash
kubectl apply -k kustomize
```

This applies:

* Deployment
* Service
* Ingress

---

##  HPA (Auto-Scaling)

The app scales based on CPU usage using Kubernetes HPA.

Check status:

```bash
kubectl get hpa -n uptime-dev
```

> Since this is a lightweight demo app, CPU rarely exceeds the threshold — this setup is primarily to demonstrate production patterns.

---

## ⏱️ CronJob Behaviour

The CronJob:

* Runs at a scheduled interval
* Retries on failure up to a defined backoff limit
* Uses a dedicated ServiceAccount with least-privilege RBAC

---

##  Security

* **RBAC:** Scoped ServiceAccount for scheduled workloads
* **NetworkPolicy:** Restricts pod-to-pod communication
* **Namespace isolation:** Workloads are contained within `uptime-dev`

---

## 🧠 CI/CD Workflow (Local Jenkins)

Pipeline stages:

1. Build Docker image
2. Tag image for local registry
3. Push to `localhost:5001`
4. Deploy using `kubectl apply -k kustomize`
5. Verify rollout

*(On Windows, batch execution (`bat`) is used instead of `sh`.)*

---

##  What This Project Demonstrates

You can confidently say in interviews:

> “I built a containerised Flask application deployed on Kubernetes with Ingress, RBAC, NetworkPolicy, StatefulSet for Postgres, HPA for scaling, and managed manifests using Kustomize. I also defined a Jenkins CI/CD pipeline to automate image builds and deployments.”




