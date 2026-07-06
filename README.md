⚛ Ground-State Energy Predictor

VQE Experiment — Hydrogen Reaction Energy

A point-and-click quantum-chemistry lab on your own computer


In One Sentence

This app uses a real quantum-computing algorithm (VQE) to predict the ground-state energy of hydrogen — and how much energy is released when two hydrogen atoms bond into a molecule — then shows the whole process with IBM-style 3D visualizations, all from a single window you click through.

What Is VQE?

VQE stands for the Variational Quantum Eigensolver.

It is one of the most important algorithms in quantum chemistry. Its job is to find the lowest possible energy of a molecule — its "ground state" — which tells us how stable the molecule is and how it will behave.

How it works, in plain English:


A quantum circuit prepares a guess for the molecule's state.
The energy of that guess is measured.
A classical optimizer nudges the circuit's dials to lower the energy.
Repeat steps 1–3 until the energy stops dropping.


The final, lowest energy is the answer. It is a "trial and error" dance between a quantum computer (which explores states) and an ordinary computer (which decides what to try next). This teamwork is why VQE runs well on today's small, noisy quantum hardware.

What This Project Actually Computes

The experiment runs three steps and reports the results in hartree (the standard unit of energy in chemistry):

StepComputationQubits1Ground-state energy of a single hydrogen atom12Ground-state energy of a hydrogen molecule, H₂23The reaction energy of H + H → H₂—

The reaction energy answers a real chemistry question: how much energy is given off when two hydrogen atoms snap together into a molecule? A negative number means energy is released (the molecule is more stable than two loose atoms — which is exactly why hydrogen gas exists as H₂).

For comparison, the app also computes the exact answer the "old-fashioned" way (classical linear algebra), so you can see how close the quantum algorithm gets.

The Pictures It Draws

Just like IBM's own quantum tools:


Convergence graphs — line charts showing the energy dropping, step by step, until it settles onto the exact answer. This is the algorithm "learning."
3D energy landscape — a colorful 3D surface of the energy across the circuit's dials. The red dot marks the valley — the lowest-energy solution the algorithm found. You can drag to rotate it.
Density-matrix "cityscape" — the iconic IBM 3D bar chart of the final quantum state — a skyline of bars describing exactly what the qubits are doing.
Bloch spheres — the classic 3D globe view of each qubit's state.


Two Ways to Run It

🖥 Local Simulator (default — recommended)

Free. Runs entirely on your own computer. No account, no sign-up, no internet needed after setup. Perfect for learning.

🌐 Real IBM Quantum Computer

Sends the same job over the internet to an actual quantum processor at IBM. Requires a free IBM Quantum account (an API key + instance CRN) and uses your account's usage quota.

What's in This Repository

FilePurposeRun_VQE_App.commandDouble-click this to launch the app (easiest way)HOW_TO_RUN.txtStep-by-step running instructions for beginnersABOUT.txtWhat the project is and doesvqe_code.pyThe entire program in one file: the quantum VQE algorithm plus the point-and-click window. Run it directly with python3 vqe_code.py

Quick Start

bash# 1. Install dependencies (one time)
pip install qiskit qiskit-aer qiskit-ibm-runtime scipy matplotlib numpy

# 2. Run the app
python3 vqe_code.py

Then pick Local simulator, click Run experiment, and watch it converge.

Built With

ToolRoleQiskitIBM's open-source quantum computing frameworkQiskit AerThe local quantum simulatorQiskit IBM RuntimeThe bridge to real IBM quantum hardwareSciPyThe classical optimizer that guides the searchNumPyThe math engineMatplotlibThe 2D and 3D graphsTkinterThe point-and-click window

Why It Matters

Simulating molecules is one of the most promising real-world uses of quantum computers. Even this tiny hydrogen example is the same kind of calculation researchers hope to one day scale up to design new medicines, batteries, catalysts, and materials — problems that are extremely hard for ordinary computers. This project lets you watch that idea in action, hands-on, with nothing but a click.


New here? Open HOW_TO_RUN.txt next.
