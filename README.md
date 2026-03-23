This project implements a fully containerised uptime and observability stack deployed on a local Kubernetes cluster. It brings together a Flask application, Nginx edge service, PostgreSQL database, and multiple scheduled jobs for metrics, log processing, and alerting. All components run on Docker and are orchestrated using Kubernetes with Ingress, TLS, HPA, RBAC, NetworkPolicies, and StatefulSets.

A complete CI/CD pipeline is provided using Jenkins running locally in Docker. The pipeline performs linting, testing, container image builds, Trivy vulnerability scanning, pushes to a local registry, and automated deployments using Kustomize overlays — simulating a realistic production workflow entirely in a local environment.

This repository is structured to follow industry-standard DevOps practices and serves as an end-to-end hands-on project covering containerisation, orchestration, automation, observability, and reliability engineering.
