╔══════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║        ⚛  GROUND-STATE ENERGY PREDICTOR  ⚛                                 ║
║        VQE Experiment — Hydrogen Reaction Energy                           ║
║                                                                            ║
║        A point-and-click quantum-chemistry lab on your own computer        ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝


┌────────────────────────────────────────────────────────────────────────────┐
│  IN ONE SENTENCE                                                           │
└────────────────────────────────────────────────────────────────────────────┘

   This app uses a real quantum-computing algorithm (VQE) to predict the
   ground-state energy of hydrogen — and how much energy is released when
   two hydrogen atoms bond into a molecule — then shows the whole process
   with beautiful IBM-style 3D visualizations, all from a single window you
   click through.


┌────────────────────────────────────────────────────────────────────────────┐
│  WHAT IS VQE?                                                              │
└────────────────────────────────────────────────────────────────────────────┘

   VQE stands for the "Variational Quantum Eigensolver."

   It is one of the most important algorithms in quantum chemistry. Its job
   is to find the LOWEST possible energy of a molecule — its "ground state" —
   which tells us how stable the molecule is and how it will behave.

   How it works, in plain English:

      1.  A quantum circuit prepares a guess for the molecule's state.
      2.  The energy of that guess is measured.
      3.  A classical optimizer nudges the circuit's dials to lower the
          energy.
      4.  Repeat steps 1–3 until the energy stops dropping.

   The final, lowest energy is the answer. It is a "trial and error" dance
   between a quantum computer (which explores states) and an ordinary
   computer (which decides what to try next). This teamwork is why VQE runs
   well on today's small, noisy quantum hardware.


┌────────────────────────────────────────────────────────────────────────────┐
│  WHAT THIS PROJECT ACTUALLY COMPUTES                                      │
└────────────────────────────────────────────────────────────────────────────┘

   The experiment runs three steps and reports the results in "hartree"
   (the standard unit of energy in chemistry):

      •  STEP 1 — Ground-state energy of a single HYDROGEN ATOM  (1 qubit)
      •  STEP 2 — Ground-state energy of a HYDROGEN MOLECULE, H₂  (2 qubits)
      •  STEP 3 — The REACTION ENERGY of  H + H → H₂

   The reaction energy answers a real chemistry question: how much energy is
   given off when two hydrogen atoms snap together into a molecule? A
   negative number means energy is released (the molecule is more stable
   than two loose atoms — which is exactly why hydrogen gas exists as H₂).

   For comparison, the app also computes the exact answer the "old-fashioned"
   way (classical linear algebra), so you can see how close the quantum
   algorithm gets.


┌────────────────────────────────────────────────────────────────────────────┐
│  THE PICTURES IT DRAWS  (just like IBM's own quantum tools)               │
└────────────────────────────────────────────────────────────────────────────┘

   ▸  CONVERGENCE GRAPHS
        Line charts showing the energy dropping, step by step, until it
        settles onto the exact answer. This is the algorithm "learning."

   ▸  3D ENERGY LANDSCAPE
        A colorful 3D surface of the energy across the circuit's dials. The
        red dot marks the valley — the lowest-energy solution the algorithm
        found. You can drag to rotate it.

   ▸  DENSITY-MATRIX "CITYSCAPE"
        The iconic IBM 3D bar chart of the final quantum state — a skyline
        of bars describing exactly what the qubits are doing.

   ▸  BLOCH SPHERES
        The classic 3D globe view of each qubit's state.


┌────────────────────────────────────────────────────────────────────────────┐
│  TWO WAYS TO RUN IT                                                        │
└────────────────────────────────────────────────────────────────────────────┘

   ▸  LOCAL SIMULATOR  (default — recommended)
        Free. Runs entirely on your own computer. No account, no sign-up,
        no internet needed after setup. Perfect for learning.

   ▸  REAL IBM QUANTUM COMPUTER
        Sends the same job over the internet to an actual quantum processor
        at IBM. Requires a free IBM Quantum account (an API key + instance
        CRN) and uses your account's usage quota.


┌────────────────────────────────────────────────────────────────────────────┐
│  WHAT'S IN THIS FOLDER                                                     │
└────────────────────────────────────────────────────────────────────────────┘

   Run_VQE_App.command …… Double-click this to launch the app (easiest way).
   HOW_TO_RUN.txt …………… Step-by-step running instructions for beginners.
   ABOUT.txt ……………………… This file — what the project is and does.
   vqe_code.py ………………… The ENTIRE program in one file: the quantum VQE
                            algorithm plus the point-and-click window. Run
                            it directly with:  python3 vqe_code.py


┌────────────────────────────────────────────────────────────────────────────┐
│  BUILT WITH                                                               │
└────────────────────────────────────────────────────────────────────────────┘

   •  Qiskit …………………… IBM's open-source quantum computing framework
   •  Qiskit Aer ……………… the local quantum simulator
   •  Qiskit IBM Runtime … the bridge to real IBM quantum hardware
   •  SciPy …………………………… the classical optimizer that guides the search
   •  NumPy …………………………… the math engine
   •  Matplotlib ………………… the 2D and 3D graphs
   •  Tkinter ………………………… the point-and-click window


┌────────────────────────────────────────────────────────────────────────────┐
│  WHY IT MATTERS                                                            │
└────────────────────────────────────────────────────────────────────────────┘

   Simulating molecules is one of the most promising real-world uses of
   quantum computers. Even this tiny hydrogen example is the same kind of
   calculation researchers hope to one day scale up to design new medicines,
   batteries, catalysts, and materials — problems that are extremely hard
   for ordinary computers. This project lets you watch that idea in action,
   hands-on, with nothing but a click.


              ─────────────────────────────────────────────────
                  New here?  Open  HOW_TO_RUN.txt  next.
              ─────────────────────────────────────────────────
