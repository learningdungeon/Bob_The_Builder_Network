# Remote Anonymous Quantum Transmission (RAQT) in NetSquid

NetSquid simulation of Robust Anonymous Quantum Transmission (Christandl-Wehner 2004 protocol)

This folder provides a functional implementation of the **Remote Anonymous Quantum Transmission (RAQT)** protocol using the **NetSquid** discrete-event simulation framework.

The simulation demonstrates how a Greenberger–Horne–Zeilinger (GHZ) state can be utilized to transmit a secret bit across a network of participants while maintaining the absolute anonymity of the sender.

---

## 🔬 Protocol Logic

The RAQT protocol leverages the parity properties of entangled states. By performing measurements in the $X$-basis, the global phase shift applied by a single participant (the sender) can be recovered through the XOR sum of all outcomes.

### **The Quantum Circuit**

1.  **State Preparation**: A 4-qubit GHZ state is initialized: 
    $$\frac{1}{\sqrt{2}}(|0000\rangle + |1111\rangle)$$
2.  **Encoding**: The sender (e.g., `sender_id = 2`) applies a $Z$ gate to their local qubit if their secret bit is **1**. If the bit is **0**, no operation is performed.
3.  **Basis Transformation**: All participants apply a Hadamard ($H$) gate to rotate their qubits from the computational basis ($Z$) to the transverse basis ($X$).
4.  **Measurement**: Every participant performs a standard measurement.
5.  **Parity Check**: The XOR sum (parity) of all measurement results is calculated.

---

## 🛠 Technical Implementation

The script uses the **NetSquid Qubit API (`qapi`)** and mathematical **Operators** to verify the protocol logic in an ideal state-vector environment. This avoids the `ProcessorBusyError` associated with discrete-event timing while maintaining physical accuracy.

### **Dependencies**
* **Python**: 3.8+
* **NetSquid**: Quantum network simulator (`pip install netsquid`)

### **Core Code Structure**
```bash
RAQTNetSquid.py 
```

