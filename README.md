# Infra-lakehouse: FluxCD Bootstrap & Initialization Guide

This guide explains how to bootstrap and initialize this repository using FluxCD on any Kubernetes cluster.

---

## Prerequisites

- A running Kubernetes cluster (e.g., Minikube, Kind, AKS, EKS, GKE, etc.)
- `kubectl` installed and configured for your cluster
- [Flux CLI (optional, for convenience)](https://fluxcd.io/docs/installation/)
- Your Git repository accessible (public or with deploy key/credentials)

---

## 1. Install FluxCD Components

Apply the FluxCD core components to your cluster:

```sh
kubectl apply -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml
```

Wait until all Flux pods are running:

```sh
kubectl get pods -n flux-system
```

---


Apply both:

```sh
kubectl apply -f git-repo.yaml
kubectl apply -f root-kustomization.yaml
```

---

## 3. Wait for Flux to Reconcile

Flux will now pull your repository and apply the manifests under `./flux-config` (and any further Kustomizations defined there).

Check status:

```sh
kubectl get kustomizations -A
kubectl get gitrepositories -A
```

---

## 4. Namespace Bootstrapping

Namespaces are managed under `infrastructure/namespaces` and applied by the `namespaces-setup` Kustomization.  
Flux will automatically create all required namespaces before applying resources to them.

---

## 5. Application Deployments

All application manifests (Airflow, Prometheus, Grafana, etc.) are managed via HelmReleases and Kustomizations in their respective folders.  
Secrets should be managed via Kubernetes Secret manifests and referenced in your Helm values using `extraEnvFrom` or similar mechanisms.

---

## 6. Accessing Services

- **Airflow Webserver:**  
  Use `kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow`  
  Or, with Minikube: `minikube service airflow-webserver -n airflow`

- **Grafana/Prometheus:**  
  Use similar port-forward or Minikube service commands.

---

## 7. Troubleshooting

- Check Kustomization and HelmRelease status:
  ```sh
  kubectl get kustomizations -A
  kubectl get helmreleases -A
  ```
- View logs for Flux controllers:
  ```sh
  kubectl logs -n flux-system deploy/source-controller
  kubectl logs -n flux-system deploy/kustomize-controller
  kubectl logs -n flux-system deploy/helm-controller
  ```

---

## 8. Updating the Cluster

Push changes to your Git repository.  
Flux will automatically detect and apply them.

---

## 9. Cleaning Up

To remove Flux and all managed resources:

```sh
kubectl delete -f https://github.com/fluxcd/flux2/releases/latest/download/install.yaml
```

---

## References

- [FluxCD Documentation](https://fluxcd.io/docs/)
- [Helm Operator Docs](https://fluxcd.io/docs/components/helm/)

---