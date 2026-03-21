# Containerised Uptime Stack on Kubernetes with Local CI/CD

A production-style DevOps project that builds a fully containerised uptime monitoring system with a local Kubernetes deployment and CI/CD pipeline, running entirely without cloud dependency.

---

## Overview

This project demonstrates how to design, build, and deploy a real-world DevOps system locally. It includes containerised services, Kubernetes orchestration, CI/CD automation, and production-grade practices such as security, scaling, and reliability.

All components run on a local Kubernetes cluster using Docker Desktop with a local container registry.

---

## Goal

- Containerised applications using multi-stage Docker builds  
- Kubernetes deployment with production-grade components  
- Local CI/CD pipeline for automated build, test, and deployment  
- Monitoring, logging, and alerting using scheduled jobs  

---

## Architecture

<img width="1076" height="863" alt="image" src="https://github.com/user-attachments/assets/65783c6c-b93e-4970-b038-d32d7fdc138d" />


---

## System Components

### Application Layer
- Flask API with `/health` and `/echo`
- Graceful shutdown handling
- Liveness and readiness probes

### Edge Layer
- Nginx reverse proxy
- Custom access logs with request timing
- TLS-enabled Ingress

### Database Layer
- PostgreSQL StatefulSet
- Primary and replica (streaming replication)
- Persistent storage (PVC)

### Background Jobs
- Metrics collector (writes health data to DB)
- Log parser (processes Nginx logs)
- Alert system (SLO evaluation)

### Kubernetes Features
- Ingress with TLS
- Horizontal Pod Autoscaler (HPA)
- RBAC (least privilege)
- Network Policies (default deny)
- Pod Disruption Budgets

### CI/CD Pipeline
- Jenkins running locally in Docker

Pipeline stages: lint → test → build → scan → push → deploy → smoke → rollback


### Security
- Non-root containers
- Resource limits enforced
- Image scanning (Trivy)
- Dockerfile linting (hadolint)
- Kubernetes manifest linting

---

## Setup

### 1. Clone Repository

git clone https://github.com/Sandeepkulkarni77/Containerised-Uptime-Stack-on-Kubernetes-with-Local-CI-CD

cd Containerised-Uptime-Stack-on-Kubernetes-with-Local-CI-CD

---

### 2. Configure Environment

cp .env.example .env

Update environment variables as required.

---

### 3. Run Local Development

docker compose up --build -d

Test:

curl http://localhost:5000/health

---

### 4. Deploy to Kubernetes

kubectl apply -f k8s/base/namespace.yaml  
bash scripts/load-secrets.sh  
kubectl apply -k k8s/overlays/dev  

---

### 5. Access Application

curl -k https://uptime.local/health  

(Add `uptime.local` to `/etc/hosts` if required)

---

## CI/CD

Start Jenkins:

make ci

Access Jenkins:

http://localhost:8090

---

## Features

- Fully local DevOps setup (no cloud dependency)
- End-to-end CI/CD pipeline
- Auto-scaling using HPA
- Zero-downtime deployment strategy
- Production-like architecture
- Secure container and Kubernetes practices

---

## Security Practices

- Containers run as non-root
- Image scanning using Trivy
- Dockerfile linting using hadolint
- Kubernetes manifest validation
- Network isolation using policies
- Secrets managed securely

---

## Testing

- Unit tests executed during Docker build
- Smoke tests after deployment
- Load testing for autoscaling validation
- Automatic rollback on failure

---

## Common Issues

- ImagePullBackOff: Ensure images are pushed to local registry  
- Missing secrets: Run `load-secrets.sh` before deployment  
- Port conflicts: Change ports if already in use  
- Ingress issues: Verify DNS and TLS configuration  

---

## Learning Outcomes

- End-to-end DevOps workflow
- Kubernetes architecture and deployment patterns
- CI/CD pipeline implementation
- Security best practices
- Scaling and reliability engineering

---

## Notes

- Runs fully locally (offline or LAN)
- No dependency on cloud providers
- Designed to simulate production-grade systems on a local machine






