# CIA Project Status

**Last Completed Step:** Этап 1.1: Подготовка GPU-ноды в K8s и установка NVIDIA GPU Operator

**Current Step:** Этап 1.2.1: Развертывание Kubeflow

**Next Step:** Этап 1.2.2: Развертывание Qdrant

---

## 🧠 Key Context Reminders:
- **Persona:** Senior DevOps Engineer, learning LLMOps.
- **Core Tech:** K8s, Terraform, KFP, vLLM, Langfuse, DeepEval.
- **Method:** Explain ML concepts via DevOps analogies.
- **Goal:** Build a self-hosted Code Intelligence Assistant.

---

## 📝 Project Artifacts & Notes

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