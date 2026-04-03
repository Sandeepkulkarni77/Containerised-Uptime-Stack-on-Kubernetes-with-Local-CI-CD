#  Containerised Uptime Stack on Kubernetes with Local CI/CD

> A fully offline, production-grade uptime and log intelligence stack running on local Kubernetes with a complete CI/CD pipeline.

---

## Overview

This project transforms a "Prod-Lite Uptime & Log Intelligence Stack" into a fully containerised, locally-orchestrated system. It runs entirely **offline or LAN-only** — no cloud required.

**What this project delivers:**

- Multi-stage, non-root Docker images with security scanning
- Local Kubernetes cluster (minikube or kind) with Ingress, TLS, StatefulSet DB, CronJobs, HPA, RBAC, and NetworkPolicies
- Local CI/CD pipeline via Jenkins-in-Docker that builds, scans, tests, and deploys to the cluster
- A local container registry (no DockerHub, no cloud registry)

---

## Architecture


<img width="1076" height="863" alt="Screenshot 2026-03-21 224734" src="https://github.com/user-attachments/assets/6e9d6abd-b480-455c-ad96-652f0b18a327" />

---

## Project Structure

```
zero-to-prod-k8s/
├── app/                          # Flask application + tests
│   ├── Dockerfile                # Multi-stage, non-root build
│   └── src/
│       ├── main.py
│       └── tests/
├── edge/                         # Nginx reverse proxy
│   ├── Dockerfile
│   └── nginx.conf                # Custom log format with $request_time
├── jobs/                         # Background jobs
│   ├── metrics/                  # Healthcheck CronJob → writes to Postgres
│   ├── log-parser/               # Regex log parser → daily CSV in PVC
│   └── alerts/                   # SLO breach evaluator → webhook / file
├── k8s/
│   ├── base/                     # Kustomize base manifests
│   │   ├── namespace.yaml
│   │   ├── edge/                 # Service, Ingress, ConfigMap, Secret
│   │   ├── app/                  # Deployment, Service, ConfigMap, HPA
│   │   ├── jobs/                 # CronJob manifests
│   │   ├── db/                   # StatefulSet, Service, PVC
│   │   ├── rbac/                 # ServiceAccounts, Roles, RoleBindings
│   │   ├── netpol/               # NetworkPolicies
│   │   └── issuer/               # cert-manager SelfSigned ClusterIssuer
│   └── overlays/
│       └── dev/                  # Image tags, replica counts, env overrides
├── ci/
│   ├── Jenkinsfile               # Pipeline-as-code (lint→test→build→scan→deploy→smoke)
│   └── docker-compose.ci.yml     # Jenkins + local runner + registry
├── registry/
│   └── compose.yml               # Local registry:2 + optional UI
├── scripts/
│   ├── kind-up.sh                # Spin up kind cluster
│   ├── minikube-up.sh            # Spin up minikube cluster
│   ├── connect-registry.sh       # Wire local registry to cluster
│   ├── load-secrets.sh           # Create K8s Secrets from .env files
│   ├── rollout.sh                # Blue/green or canary deployment
│   └── smoke.sh                  # curl tests + K8s readiness checks
├── policies/
│   └── kyverno/                  # (Stretch) Deny pods without resource limits
├── docs/
│   ├── architecture.md
│   ├── runbook.md
│   ├── troubleshooting.md
│   └── screenshots/
├── Makefile
├── .hadolint.yaml                # Dockerfile linting config
├── .kube-linter-config.yaml      # Manifest linting config
├── .trivyignore                  # Known-safe CVE exceptions
└── README.md
```

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24+ | Container builds and local CI |
| kind or minikube | latest | Local Kubernetes cluster |
| kubectl | 1.28+ | Cluster management |
| kustomize | 5+ | Manifest overlays |
| helm | 3+ | Optional (Bitnami Postgres HA) |
| mkcert | latest | Local TLS certificates |
| make | any | Task runner |

**Install cluster tooling:**

```bash
# kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && chmod +x ./kind

# or minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

## Quick Start

### 1. Spin up the local cluster

```bash
# Using Docker Dekstop (recommended)
make cluster-up
```

### 2. Start the local container registry

```bash
cd registry && docker compose up -d
bash scripts/connect-registry.sh
```

### 3. Build and push all images

```bash
make build-all
make push-all
```

### 4. Load secrets into the cluster

```bash
# Copy .env.example to .env and fill in values
cp .env.example .env
bash scripts/load-secrets.sh
```

### 5. Deploy to Kubernetes

```bash
kubectl apply -k k8s/overlays/dev
kubectl rollout status deployment/app -n uptime-dev
```

### 6. Run smoke tests

```bash
bash scripts/smoke.sh
```

### 7. Start the CI/CD pipeline (Jenkins)

```bash
cd ci && docker compose -f docker-compose.ci.yml up -d
# Access Jenkins at http://localhost:8080
```

---

## Components

### `edge` — Nginx Reverse Proxy

- Exposed via `ingress-nginx` with TLS terminated at the Ingress
- Custom log format including `$request_time` for latency tracking
- Logs mounted via `emptyDir` shared with the `log-parser` job

### `app` — Flask Service

- Endpoints: `GET /health`, `POST /echo`
- Liveness probe: `/health` (strict thresholds)
- Readiness probe: `/health` (allows traffic only when ready)
- `terminationGracePeriodSeconds: 10` for graceful shutdown
- Resource requests and limits enforced
- HPA: CPU target 50–60%, min 1 / max 3 replicas

### `metrics-job` — CronJob

- Python healthcheck script
- Polls the app's `/health` endpoint and writes results to PostgreSQL

### `log-parser` — CronJob

- Regex-based Nginx access log parser
- Reads logs from a shared volume (emptyDir or sidecar copy)
- Produces a daily CSV file written to a PVC

### `alerts` — CronJob / Job

- Evaluates SLO breach conditions from the DB
- Posts to a local webhook endpoint or writes to a file

### `db` — PostgreSQL StatefulSet

- 1 primary + 1 streaming replica
- PVCs for persistent data storage
- Can optionally use `bitnami/postgresql-ha` Helm chart

---

## Kubernetes Setup

### Cluster Components

| Component | Purpose |
|-----------|---------|
| `ingress-nginx` | Ingress controller |
| `cert-manager` | Automated TLS (SelfSigned ClusterIssuer) |
| `local-path-provisioner` | Dynamic PVC provisioning |
| `metrics-server` | Resource metrics for HPA |

### Install cluster add-ons

```bash
# ingress-nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### RBAC Design

Each job runs under a dedicated `ServiceAccount` with least-privilege `Role` bindings. No job has cluster-wide access.

### NetworkPolicy Rules

| Source | Destination | Allowed |
|--------|-------------|---------|
| `edge` | `app` | ✅ |
| `app` | `db` | ✅ |
| `jobs` | `db` | ✅ |
| All others | All | ❌ (default deny) |

### Verify the deployment

```bash
# Check all pods
kubectl get pods -n uptime-dev

# Verify TLS on Ingress
kubectl describe ingress -n uptime-dev

# Check replica DB recovery status
kubectl exec -n uptime-dev db-replica-0 -- psql -U postgres -c "SELECT pg_is_in_recovery();"

# Test HPA
kubectl top pods -n uptime-dev
# Load test with hey:
hey -n 10000 -c 100 https://localhost/app/health
kubectl get hpa -n uptime-dev -w
```

---

## CI/CD Pipeline

The pipeline is defined in `ci/Jenkinsfile` and runs against the local cluster.

### Pipeline Stages

<img width="1416" height="609" alt="image" src="https://github.com/user-attachments/assets/f7cfffcf-f237-48de-a3c6-df48869a64fa" />
                    
### Image Tagging Convention

All images are tagged with the Git SHA:

```
localhost:5001/uptime/<service>:<git-sha>
```

### Start Jenkins

```bash
cd ci
docker compose -f docker-compose.ci.yml up -d
```

Jenkins mounts `/var/run/docker.sock` for Docker builds. The kubeconfig is injected as a Jenkins Secret and mounted read-only into the pipeline.

---

## Security & Policies

### Container Hardening

- Multi-stage builds — only runtime artifacts in final image
- Non-root user: `USER 10001`
- `WORKDIR /app`
- `HEALTHCHECK` defined in every Dockerfile
- Target image size: **< 150 MB** for `app`
- Trivy scan: **fail pipeline on HIGH or CRITICAL CVEs**

### Dockerfile Linting

```bash
hadolint --config .hadolint.yaml app/Dockerfile
```

### Manifest Linting

```bash
kube-linter lint k8s/ --config .kube-linter-config.yaml
```

### Resilience Features

| Feature | Description |
|---------|-------------|
| `PodDisruptionBudget` | Prevents full app/db outage during `kubectl drain` |
| `preStop` hook | Drains connections before the pod is killed |
| Blue/Green deployment | Zero-downtime cutover via label switch |
| HPA | Autoscales app on CPU (50–60% target) |
| Liveness probe | Kills and restarts bad pods automatically |

### Stretch: Policy Gates (Kyverno / OPA Gatekeeper)

A policy gate denies pods that:
- Lack `resources.limits`
- Run as root (missing non-root `securityContext`)

```bash
# Example: apply Kyverno policies
kubectl apply -f policies/kyverno/
```

---

## Sprint Roadmap

| Sprint | Days | Focus | Key Outcome |
|--------|------|-------|-------------|
| **Sprint 1** | 1–4 | Docker depth | Slim, non-root images; docker-compose dev loop |
| **Sprint 2** | 5–8 | Kubernetes fundamentals | Cluster up, TLS ingress, StatefulSet DB, HPA, RBAC, NetPol |
| **Sprint 3** | 9–12 | Local CI/CD | Jenkins pipeline: lint → test → build → scan → push → deploy → smoke |
| **Sprint 4** | 13–14 | Reliability & policy | PDB, blue/green, policy gates, resilience drills |

---

## Acceptance Criteria

### Sprint 1 — Docker

```bash
# Image size check
docker images | grep uptime/app   # target < 150MB

# Trivy scan
trivy image localhost:5001/uptime/app:latest --exit-code 1 --severity HIGH,CRITICAL

# Local TLS
curl -k https://localhost/app/health   # 200 OK
```

### Sprint 2 — Kubernetes

```bash
kubectl get pods -n uptime-dev                          # all Running
kubectl describe ingress -n uptime-dev                  # TLS visible
kubectl port-forward svc/app 8080:80 -n uptime-dev &
curl http://localhost:8080/health                        # 200 OK
kubectl top pods -n uptime-dev                          # metrics-server working
```

### Sprint 3 — CI/CD

```bash
# Check rollout history
kubectl rollout history deployment/app -n uptime-dev

# Force failure test → rollback should trigger automatically
```

### Sprint 4 — Reliability

```bash
# PDB prevents outage during drain
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data

# Policy gate rejects bad manifest
kubectl apply -f test/bad-pod-no-limits.yaml   # should be denied

# Blue/green cutover
bash scripts/rollout.sh blue-green
```

---

## Makefile Reference

```bash
make cluster-up        # Start local K8s cluster
make cluster-down      # Tear down cluster
make registry-up       # Start local container registry
make build-all         # Build all images
make push-all          # Push all images to local registry
make deploy            # Apply Kustomize overlays
make smoke             # Run smoke tests
make lint              # Run hadolint + kube-linter
make scan              # Run Trivy on all images
make ci-up             # Start Jenkins CI stack
make clean             # Remove all local resources
```

---

## Docs

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | Full system design and component interaction |
| [`docs/runbook.md`](docs/runbook.md) | Operational procedures and common tasks |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Debugging guide for common issues |
| [`docs/screenshots/`](docs/screenshots/) | Visual evidence of working components |

---

## Environment Variables

Never commit secrets. Use `.env` files (gitignored) and load them with:

```bash
bash scripts/load-secrets.sh
```

See `.env.example` for required variables:

```bash
POSTGRES_USER=uptime
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=uptimedb
WEBHOOK_URL=http://localhost:9000/hooks/alert
REGISTRY=localhost:5001
```

---


