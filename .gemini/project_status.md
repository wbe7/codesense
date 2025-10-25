# CIA Project Status

**Last Completed Step:** None

**Current Step:** Этап 1.1: YC GPU-Кластер (Terraform)

**Next Step:** Этап 1.2: Локальный стек

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

