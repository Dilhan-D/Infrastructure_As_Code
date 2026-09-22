# Infrastructure as code

![Docker](https://img.shields.io/badge/docker-v29.6-blue)
![WSL](https://img.shields.io/badge/WSL-v2.7-white)
![Kubernetes](https://img.shields.io/badge/kubernetes-version..-green)
![Terraform](https://img.shields.io/badge/terraform-version..-purple)
![Ansible](https://img.shields.io/badge/ansible-version..-red)
![SQL](https://img.shields.io/badge/sql-postgres..-orange)

Infrastructure as Code" repository containing my Terraform, Kubernetes, Docker, and Ansible projects.

I'm starting my learning with Docker: I installed Docker Desktop and WSL since I'm working on a Windows environment.

The project includes a Python application with an HTML interface designed to containerize using Docker and Docker Compose. The app is structured to allow for future integration with a PostgreSQL database (pulled from Docker Hub) and potential connection to additional services as the learning progresses.

This is an ongoing learning process. this repository will evolve as I explore new tools, best practices, and automation techniques.

## Demarrage local

Copiez `.env.example` vers `.env`, adaptez les valeurs, puis lancez :

```bash
docker compose -f docker/compose.yaml up --build
```

L'application est disponible sur `http://localhost:5000` et Adminer sur `http://localhost:8080`.

## Kubernetes

Construisez l'image, rendez-la disponible dans votre cluster local, puis appliquez les manifests :

```bash
docker build -t boursoum:latest -f docker/Dockerfile_app .
kubectl apply -k k8s/
kubectl get pods -n boursoum
```

Le mot de passe Kubernetes dans `k8s/config.yaml` est un exemple à remplacer avant un déploiement réel.

## Ansible

Le playbook `ansible/deploy.yml` installe Docker sur l'hôte cible et démarre le Compose :

```bash
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml --ask-become-pass
```

---

*Note: This project is constantly evolving and subject to change. Components may be modified, improved, or removed as my learning progresses and best practices are applied.*