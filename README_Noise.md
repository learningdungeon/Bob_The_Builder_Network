# Noisy RAQT: Resource-Aware Quantum Teleportation under Hardware Constraints

## Quantum System Architect | IBM Qiskit Advocate | Quantum Networks

This repository contains a **NetSquid** implementation of the Resource-Aware Quantum Teleportation (RAQT) protocol. This research focuses on analyzing protocol performance under realistic hardware noise models, specifically tailored for environments with non-ideal fiber-optic infrastructure.

---

### 🧪 Project Overview
While theoretical quantum protocols assume perfect execution, real-world deployment faces significant "noise." This implementation introduces a granular **Depolarizing Noise Model** to account for:

* **Gate Infidelity:** Modeling errors during foundational $H$ and $CNOT$ operations.
* **Environmental Decoherence:** Simulating $T_1/T_2$ relaxation effects during entanglement distribution.
* **Channel Noise:** Real-world simulation of data loss in regional fiber backbones.

### 📊 Reality-Based Benchmarking
Under hardware-inspired noise parameters (Gate error: 2%, Channel decoherence: 5%), the protocol currently achieves:

> **Protocol Fidelity: 82.00%**

This result underscores the critical need for **Quantum Repeaters** and hardware-aware noise mitigation in developing the global Quantum Internet.

---

### 🛠️ Technical Stack
* **Framework:** NetSquid (Network Simulator for Quantum Information Networks)
* **Language:** Python 3.10
* **OS:** Ubuntu (Linux) / WSL
* **Core Logic:** GHZ State Generation, Multipartite Entanglement, XOR Parity Reconstruction.

### 🚀 Execution
1.  **Activate Environment:**
    ```bash
    source netsquid_env/bin/activate
    ```
2.  **Run Simulation:**
    ```bash
    python "Noisy RAQT.py"
    ```

---

### 📢 Professional Vision
This work is part of a 4-tier pedagogical and research framework designed to bridge the gap between advanced quantum engineering and accessible STEM education. By modeling noise realistically, we can advocate for the specific infrastructure upgrades needed for the inevitable transition to quantum-secure networking.

**Author:** Noor Ul Ain  
**Role:** Quantum System Architect | IBM Qiskit Advocate | Quantum Networks
