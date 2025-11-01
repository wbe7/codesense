# CIA Project Status

**Last Completed Step:** Этап 1.2.3: Развертывание Langfuse

**Current Step:** Этап 1.3: Код как датасет

**Next Step:** Этап 1.4: DVC-версионирование

---

## 🧠 Key Context Reminders:
- **Persona:** Senior DevOps Engineer, learning LLMOps.
- **Core Tech:** K8s, Terraform, KFP, vLLM, Langfuse, DeepEval.
- **Method:** Explain ML concepts via DevOps analogies.
- **Goal:** Build a self-hosted Code Intelligence Assistant.

---

## 📝 Project Artifacts & Notes

### Langfuse Deployment (Completed 2025-11-01)

- **Deployment:** Deployed Langfuse using the official Helm chart.
- **Namespace:** `langfuse`
- **Ingress:** `langfuse.cloudnative.space` secured with a Cloudflare certificate via cert-manager.
- **SSO:** Configured with Deckhouse Dex as a custom OIDC provider. The `OAuthCallbackError: state mismatch` was resolved by setting `AUTH_CUSTOM_CHECKS: "state"` in the `values.yaml`.
- **Storage:** External S3 bucket `langfuse` on `192.168.77.7:9000`.
- **Persistence:** `freenas-nfs-csi` used for PostgreSQL, ClickHouse, and Redis.
- **Configuration:** Stored in `infra/langfuse/values.yaml`.

### Qdrant Deployment Validation (Completed 2025-11-01)

- **Validation:** Successfully tested the Qdrant deployment by running the test scripts in `infra/qdrant/test`.
- **Scripts:** `insert_data.py`, `search_data.py`, and `cleanup_data.py` all executed without errors.
- **Confirmation:** This confirms that the Qdrant cluster is operational and accessible via its ingress.

### Qdrant Deployment (Completed 2025-11-01)

- **Deployment:** Deployed Qdrant cluster using the official Helm chart.
- **Namespace:** `qdrant`
- **Ingress:** `qdrant.cloudnative.space` secured with a Cloudflare certificate via cert-manager.
- **Storage:** `freenas-nfs-csi` used for persistence.
- **Configuration:** Stored in `infra/qdrant/values.yaml`.

### Hardware & Model Strategy (Agreed on 2025-10-25)

- **Initial Hardware:** The project will start using a laptop with an **NVIDIA 3050 4GB** as the primary Kubernetes GPU worker node.
- **Future Hardware:** We plan to later introduce a more powerful node with an **NVIDIA 3060 12GB** GPU. This will allow for a direct performance and quality comparison.
- **Initial Model Strategy:** Due to the 4GB VRAM constraint, we will select a small but state-of-the-art model (e.g., `TinyLlama-1.1B`, `CodeGemma-2B`, or a better alternative available as of Oct 2025). The goal is to have a model small enough for fine-tuning and inference on the available hardware.
- **Model Progression:** The initial small model will allow us to build and validate the entire MLOps pipeline end-to-end. After upgrading the hardware, we will switch to a larger, more capable model (~8B parameters). This will provide a clear case study on how model size impacts performance and answer quality within the same infrastructure.
- **Iterative Re-training:** The system is designed for iterative improvement. Model interactions will be logged and traced in Langfuse. This data will be periodically reviewed to create new, high-quality training examples, which will be used to re-run the fine-tuning pipeline and deploy improved model versions.

### GPU Node Setup (Completed 2025-10-27)

- **GPU Node:** `kube-gpu-small-1` (NVIDIA GeForce RTX 3050 Laptop GPU, 4GB VRAM) successfully integrated into the Kubernetes cluster.
- **GPU Management:** NVIDIA GPU Operator installed and configured for automated driver, container toolkit, and device plugin management.
- **GPU Configuration:**
    - `gpu-small` NodeGroup configured for **Time-Slicing** (4 virtual GPUs).
    - `gpu-standard` NodeGroup configured for **Exclusive** access.
- **Deckhouse Integration:** Resolved `admission-policy-engine` conflict by labeling `gpu-operator` namespace with `security.deckhouse.io/pod-policy=privileged`.
- **Validation:** Confirmed GPU resource allocation (`nvidia.com/gpu: 4`) and successful execution of CUDA workloads via a test pod.

### deployKF Configuration (Completed 2025-10-29)

- **`values.yaml` Configuration:**
    - `argocd.source.repo.url`: `https://github.com/wbe7/codesense.git`
    - `argocd.source.repo.revision`: `main`
    - `argocd.source.repo.path`: `infra/deploykf/manifests`
    - `deploykf_dependencies.cert_manager.clusterIssuer.issuerName`: `cloudflare`
    - `deploykf_core.deploykf_istio_gateway.gateway.hostname`: `deploykf.cloudnative.space`
    - `deploykf_core.deploykf_istio_gateway.gatewayService.loadBalancerIP`: `192.168.77.207`
    - `deploykf_opt.deploykf_minio.enabled`: `false` (using external S3)
    - `deploykf_opt.deploykf_mysql.persistence.storageClass`: `freenas-nfs-csi`
    - `deploykf_core.deploykf_auth.valuesOverrides` for `generate.kubectlImage.repository`: `docker.io/bitnamilegacy/kubectl`
    - `deploykf_opt.deploykf_mysql.valuesOverrides` for `generate.kubectlImage.repository`: `docker.io/bitnamilegacy/kubectl`
- **ArgoCD Installation:**
    - `install_argocd.sh` and `sync_argocd_apps.sh` scripts moved to `infra/deploykf/`.
    - `argocd-install` directory created with necessary plugin files.
    - `assets-pvc.yaml` updated with `storageClassName: freenas-nfs-csi`.
    - `argocd` CLI installed via Homebrew.
    - `app-of-apps.yaml` applied to create the main ArgoCD application.
- **Cert-Manager Configuration:**
    - `ModuleConfig` for `cert-manager` applied with Cloudflare API token and email.
    - `cloudflare` ClusterIssuer successfully created by Deckhouse.
- **DNS Configuration:**
    - `cloudnative.space` domain fully delegated to Cloudflare.
    - `A` record for `*.deploykf.cloudnative.space` configured to point to the external IP.
- **Troubleshooting Notes:**
    - Added instructions to `infra/deploykf/README.md` for manually labeling `deploykf-auth` and `deploykf-dashboard` namespaces with `security.deckhouse.io/pod-policy=privileged` to resolve admission webhook errors.

### Kubeflow Deployment Troubleshooting (Completed 2025-10-30)

- **Issue 1: `ml-pipeline-ui-artifact` pod stuck due to missing secret `cloned--pipelines-object-store-auth` in `team-1-prod`.**
    - **Root Cause:**
        - Kyverno `ClusterPolicy` `argo-workflows--clone-bucket-secret` was cloning the secret with an incorrect name (`cloned--kubeflow-pipelines--backend-object-store-auth`) and only to `kubeflow-argo-workflows` namespace, not to profile namespaces.
        - `deploykf`'s `values.yaml` was configured for `accessKey` and `secretKey`, but the pod expected `access_key` and `secret_key`.
    - **Resolution:**
        - Updated `infra/deploykf/values.yaml`:
            - `kubeflow_tools.pipelines.objectStore.auth.existingSecretAccessKeyKey` set to `access_key`.
            - `kubeflow_tools.pipelines.objectStore.auth.existingSecretSecretKeyKey` set to `secret_key`.
        - Created custom Kyverno `ClusterPolicy` (`infra/deploykf/fix-secret-cloning-policy.yaml`) to correctly clone `deploykf-s3-credentials` from `kubeflow` to namespaces with label `pipelines.kubeflow.org/enabled: "true"` under the name `cloned--pipelines-object-store-auth`.
        - User re-created `deploykf-s3-credentials` with correct key names (`access_key`, `secret_key`).
        - Applied the custom `ClusterPolicy`.
        - Regenerated manifests and synced ArgoCD.

- **Issue 2: `ml-pipeline-ui-artifact` pod stuck due to `tls: failed to verify certificate: x509: certificate signed by unknown authority` from `poddefaults-webhook`.**
    - **Root Cause:**
        - `MutatingWebhookConfiguration` for `poddefaults-webhook` had an empty `caBundle`.
        - `cert-manager-cainjector` was disabled in Deckhouse, preventing `caBundle` injection.
        - The `Certificate` resource for the webhook was configured to use a local `Issuer` instead of a trusted `ClusterIssuer`.
    - **Resolution:**
        - Re-enabled `kubeflow_tools.poddefaults_webhook` in `infra/deploykf/values.yaml`.
        - User enabled `enableCAInjector: true` in Deckhouse `cert-manager` module configuration.
        - Deleted and recreated the `MutatingWebhookConfiguration` `admission-webhook-mutating-webhook-configuration` to force `cert-manager-cainjector` to inject the `caBundle`.
        - Verified `caBundle` injection and pod status.

### Deckhouse Dex Integration (Completed 2025-10-31)

- **Integration Strategy:** Configured `deploykf`'s internal Dex to use the existing Deckhouse Dex as an external OIDC provider.
- **`DexClient` Creation:** Created a `DexClient` resource for `deploykf` in the `deploykf-auth` namespace. This generated a `clientID` (`dex-client-deploykf@deploykf-auth`) and a `clientSecret`.
- **OIDC Connector Configuration:**
    - The OIDC connector configuration was stored in a Kubernetes Secret (`deploykf-dex-connector-config`) to avoid hardcoding secrets in `values.yaml`.
    - `values.yaml` was updated to reference this secret using `configExistingSecret` and `configExistingSecretKey`.
    - `issuer` URL was set to `https://dex.cloudnative.space/` (with a trailing slash).
    - `redirectURI` was set to `https://deploykf.cloudnative.space:8443/dex/callback`.
- **User Authorization:**
    - Defined the user `admin@skeaper.tech` in the `users` section of `values.yaml`.
    - Created `team-1--admins` and `team-1--users` groups.
    - Assigned the user to the `team-1--admins` group.
    - Configured `team-1` and `team-1-prod` profiles to grant `edit` and `view` access to the respective groups.

### Kubeflow Notebook Images (Discovered 2025-10-31)

- **Best Practice:** To avoid dependency issues (e.g., with NumPy, CUDA drivers), always use the pre-built, specialized Docker images provided by Kubeflow when creating Jupyter notebooks.
- **Example:** For GPU-accelerated TensorFlow, select an image like `kubeflownotebookswg/jupyter-tensorflow-cuda-full:v1.8.0`. This ensures that the framework, drivers, and all necessary libraries are correctly installed and configured out-of-the-box, eliminating the need for manual `pip install` commands or environment variable adjustments.