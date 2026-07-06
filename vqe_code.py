"""
vqe_all_in_one.py - The COMPLETE one-command VQE app in a single file.

This one file contains everything: the quantum computing logic AND the
point-and-click window. It is the merged version of vqe_core.py + vqe_app.py,
so you don't need any other file to run it.

WHAT THIS IS
------------
A point-and-click window for running the IBM VQE tutorial (ground-state
energy of a hydrogen atom and an H2 molecule, plus the H + H -> H2 reaction
energy) without editing any code. It also draws IBM-style 3D plots.

HOW TO RUN (one command)
------------------------
1. Install dependencies (one time, in your terminal):
       pip install qiskit qiskit-aer qiskit-ibm-runtime scipy matplotlib numpy
2. Run:
       python vqe_all_in_one.py

MODES
-----
- "Local simulator" (default): free, runs on your own computer, no account
  needed. Great for learning and testing.
- "Real IBM hardware": sends jobs to an actual quantum computer. Needs an
  IBM Quantum API key + instance CRN, and uses your account quota.
"""

import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

import numpy as np
from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import SparsePauliOp


# ======================================================================
# PART 1: CORE VQE LOGIC (originally vqe_core.py)
# ======================================================================

# ----------------------------------------------------------------------
# Problem definitions
# ----------------------------------------------------------------------

def hydrogen_atom_hamiltonian():
    """1-qubit Hamiltonian for a hydrogen atom (STO-3G basis, parity mapping)."""
    return SparsePauliOp.from_list([("I", -0.2355), ("Z", 0.2355)])


def hydrogen_molecule_hamiltonian():
    """2-qubit Hamiltonian for the H2 molecule at ~0.7414 Angstroms."""
    return SparsePauliOp.from_list([
        ("II", -1.052373245772859),
        ("IZ", 0.39793742484318045),
        ("ZI", -0.39793742484318045),
        ("ZZ", -0.01128010425623538),
        ("XX", 0.18093119978423156),
    ])


def exact_ground_state_energy(hamiltonian):
    """Classically compute the exact lowest eigenvalue for reference."""
    matrix = np.array(hamiltonian.to_matrix())
    eigenvalues = np.linalg.eigvals(matrix)
    return float(min(eigenvalues.real))


def hydrogen_atom_ansatz():
    """3-parameter single-qubit ansatz: RX - RZ - RX."""
    theta = Parameter("theta")
    phi = Parameter("phi")
    lam = Parameter("lam")
    qc = QuantumCircuit(1)
    qc.rx(theta, 0)
    qc.rz(phi, 0)
    qc.rx(lam, 0)
    return qc


def hydrogen_molecule_ansatz():
    """Standard TwoLocal ansatz for the 2-qubit H2 problem."""
    return TwoLocal(
        num_qubits=2,
        rotation_blocks=["ry", "rz"],
        entanglement_blocks="cx",
        reps=2,
        insert_barriers=True,
    )


# ----------------------------------------------------------------------
# Backend / estimator setup
# ----------------------------------------------------------------------

def make_local_estimator(shots=None, seed=None):
    """
    Local Aer simulator estimator. Free, runs on your own machine,
    no account needed. shots=None gives near-exact expectation values.
    """
    from qiskit_aer.primitives import EstimatorV2 as AerEstimator
    options = {}
    if shots:
        options["default_precision"] = 1.0 / np.sqrt(shots)
    est = AerEstimator(options={"backend_options": {"seed_simulator": seed}} if seed else None)
    return est, None  # (estimator, batch) - no batch session locally


def make_ibm_estimator(token=None, instance=None, shots=10000, min_qubits=127,
                       backend_name=None, log=print):
    """
    Real IBM Quantum hardware estimator. Requires an IBM Quantum account.
    If token/instance are given, credentials are saved first.
    Returns (estimator, batch, backend). Caller must close the batch.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch
    from qiskit_ibm_runtime import EstimatorV2 as RuntimeEstimator

    if token and instance:
        log("Saving IBM Quantum credentials...")
        QiskitRuntimeService.save_account(
            channel="ibm_quantum_platform",
            instance=instance,
            token=token,
            overwrite=True,
            set_as_default=True,
        )

    log("Connecting to IBM Quantum...")
    service = QiskitRuntimeService()

    if backend_name:
        backend = service.backend(backend_name)
    else:
        log("Finding the least busy backend (this can take a moment)...")
        backend = service.least_busy(
            operational=True, simulator=False, min_num_qubits=min_qubits
        )
    log(f"Selected backend: {backend.name}")

    batch = Batch(backend=backend)
    estimator = RuntimeEstimator(mode=batch)
    estimator.options.default_shots = shots
    return estimator, batch, backend


def transpile_for_backend(circuit, hamiltonian, backend):
    """Adapt circuit + hamiltonian to a real backend's native gates/layout."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=3)
    circuit_isa = pm.run(circuit)
    hamiltonian_isa = hamiltonian.apply_layout(layout=circuit_isa.layout)
    return circuit_isa, hamiltonian_isa


# ----------------------------------------------------------------------
# VQE optimization loop
# ----------------------------------------------------------------------

def run_vqe(ansatz, hamiltonian, estimator, x0=None, maxiter=50, tol=0.01,
            log=print, label=""):
    """
    Run the VQE trial-and-error loop.
    Returns (best_energy, result_object, cost_history).
    """
    if x0 is None:
        x0 = np.random.uniform(0, 2 * np.pi, ansatz.num_parameters)

    history = {"iters": 0, "cost_history": []}

    def cost_func(params):
        pub = (ansatz, [hamiltonian], [params])
        result = estimator.run(pubs=[pub]).result()
        energy = float(result[0].data.evs[0])
        history["iters"] += 1
        history["cost_history"].append(energy)
        log(f"  {label} iteration {history['iters']}: energy = {energy:.6f} hartree")
        return energy

    result = minimize(cost_func, x0, method="cobyla",
                      options={"maxiter": maxiter, "tol": tol})
    return float(result.fun), result, history["cost_history"]


# ----------------------------------------------------------------------
# Full experiment
# ----------------------------------------------------------------------

def run_full_experiment(mode="local", maxiter=50, shots=10000,
                        token=None, instance=None, backend_name=None,
                        seed=None, log=print):
    """
    Run the complete workflow:
      1. Hydrogen atom VQE
      2. H2 molecule VQE
      3. Reaction energy H + H -> H2
    mode: "local" (free simulator) or "ibm" (real hardware).
    Returns a results dictionary.
    """
    ham_h = hydrogen_atom_hamiltonian()
    ham_h2 = hydrogen_molecule_hamiltonian()
    exact_h = exact_ground_state_energy(ham_h)
    exact_h2 = exact_ground_state_energy(ham_h2)

    log("=" * 60)
    log(f"Exact ground state energy (H atom):     {exact_h:.6f} hartree")
    log(f"Exact ground state energy (H2 molecule): {exact_h2:.6f} hartree")
    log("=" * 60)

    ansatz_h = hydrogen_atom_ansatz()
    ansatz_h2 = hydrogen_molecule_ansatz()

    batch = None
    try:
        if mode == "ibm":
            estimator, batch, backend = make_ibm_estimator(
                token=token, instance=instance, shots=shots,
                backend_name=backend_name, log=log,
            )
            log("Transpiling circuits for real hardware...")
            ansatz_h, ham_h_run = transpile_for_backend(ansatz_h, ham_h, backend)
            ansatz_h2, ham_h2_run = transpile_for_backend(ansatz_h2, ham_h2, backend)
        else:
            estimator, batch = make_local_estimator(shots=shots, seed=seed)
            ham_h_run, ham_h2_run = ham_h, ham_h2
            # The local simulator needs library circuits broken into basic gates
            ansatz_h = ansatz_h.decompose()
            ansatz_h2 = ansatz_h2.decompose()
            log("Using free local simulator (no account needed).")

        if seed is not None:
            np.random.seed(seed)

        log("")
        log("--- Step 1: VQE for the hydrogen atom ---")
        vqe_h, res_h, hist_h = run_vqe(
            ansatz_h, ham_h_run, estimator,
            x0=[1.0, 1.0, 0.0], maxiter=maxiter, log=log, label="H",
        )

        log("")
        log("--- Step 2: VQE for the H2 molecule ---")
        vqe_h2, res_h2, hist_h2 = run_vqe(
            ansatz_h2, ham_h2_run, estimator,
            maxiter=maxiter, log=log, label="H2",
        )
        params_h = np.asarray(res_h.x, dtype=float)
        params_h2 = np.asarray(res_h2.x, dtype=float)
    finally:
        if batch is not None:
            batch.close()
            log("Closed IBM Quantum batch session.")

    reaction_exact = exact_h2 - 2 * exact_h
    reaction_vqe = vqe_h2 - 2 * vqe_h

    log("")
    log("=" * 60)
    log("RESULTS")
    log("=" * 60)
    log(f"H atom energy:   exact {exact_h:.6f}  |  VQE {vqe_h:.6f} hartree")
    log(f"H2 energy:       exact {exact_h2:.6f}  |  VQE {vqe_h2:.6f} hartree")
    log(f"Reaction energy H + H -> H2:")
    log(f"                 exact {reaction_exact:.6f}  |  VQE {reaction_vqe:.6f} hartree")
    log("(negative = energy is released when the molecule forms)")

    return {
        "exact_h": exact_h, "vqe_h": vqe_h,
        "exact_h2": exact_h2, "vqe_h2": vqe_h2,
        "reaction_exact": reaction_exact, "reaction_vqe": reaction_vqe,
        "history_h": hist_h, "history_h2": hist_h2,
        "params_h": params_h, "params_h2": params_h2,
    }


# ----------------------------------------------------------------------
# Quantum-state reconstruction for 3D visualizations
# ----------------------------------------------------------------------

def final_statevector(kind, params):
    """
    Rebuild the quantum state the optimizer settled on, so it can be shown
    as an IBM-style 3D plot (Bloch sphere / density-matrix "cityscape").
    kind: "h" (hydrogen atom, 1 qubit) or "h2" (H2 molecule, 2 qubits).
    """
    from qiskit.quantum_info import Statevector
    ansatz = hydrogen_atom_ansatz() if kind == "h" else hydrogen_molecule_ansatz()
    bound = ansatz.assign_parameters(np.asarray(params, dtype=float))
    return Statevector(bound)


def hydrogen_atom_energy_surface(params, resolution=45):
    """
    Sweep two of the hydrogen-atom ansatz angles (third fixed at its
    optimized value) and evaluate the energy on a grid, producing the data
    for a 3D energy-landscape surface plot.
    Returns (grid_x, grid_y, energies, (opt_x, opt_y, opt_z), (label_x, label_y)).
    """
    from qiskit.quantum_info import Statevector
    ham = hydrogen_atom_hamiltonian()
    ansatz = hydrogen_atom_ansatz()
    plist = list(ansatz.parameters)  # deterministic (sorted) parameter order
    base = np.asarray(params, dtype=float)

    grid = np.linspace(0.0, 2.0 * np.pi, resolution)
    grid_x, grid_y = np.meshgrid(grid, grid)
    energies = np.zeros_like(grid_x)
    for i in range(resolution):
        for j in range(resolution):
            vals = base.copy()
            vals[0] = grid_x[i, j]
            vals[1] = grid_y[i, j]
            sv = Statevector(ansatz.assign_parameters(vals))
            energies[i, j] = sv.expectation_value(ham).real

    opt_z = Statevector(ansatz.assign_parameters(base)).expectation_value(ham).real
    opt = (float(base[0]), float(base[1]), float(opt_z))
    labels = (plist[0].name, plist[1].name)
    return grid_x, grid_y, energies, opt, labels


# ======================================================================
# PART 2: POINT-AND-CLICK INTERFACE (originally vqe_app.py)
# ======================================================================

class VQEApp:
    def __init__(self, root):
        self.root = root
        root.title("VQE Experiment - Hydrogen Reaction Energy")
        root.geometry("760x640")
        root.minsize(640, 560)

        self.log_queue = queue.Queue()
        self.running = False
        self.results = None

        self._build_ui()
        self._poll_log_queue()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        title = tk.Label(
            self.root,
            text="Hydrogen Reaction Energy with VQE",
            font=("Helvetica", 16, "bold"),
        )
        title.pack(pady=(10, 0))
        subtitle = tk.Label(
            self.root,
            text="Estimates ground-state energies of H and H₂, "
                 "then the H + H → H₂ reaction energy",
            font=("Helvetica", 10),
            fg="#555555",
        )
        subtitle.pack(pady=(0, 8))

        # --- Settings frame ---
        settings = ttk.LabelFrame(self.root, text="Settings")
        settings.pack(fill="x", padx=12, pady=4)

        # Mode selection
        mode_row = ttk.Frame(settings)
        mode_row.pack(fill="x", **pad)
        ttk.Label(mode_row, text="Where to run:").pack(side="left")
        self.mode_var = tk.StringVar(value="local")
        ttk.Radiobutton(
            mode_row, text="Local simulator (free, no account)",
            variable=self.mode_var, value="local",
            command=self._on_mode_change,
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            mode_row, text="Real IBM quantum computer",
            variable=self.mode_var, value="ibm",
            command=self._on_mode_change,
        ).pack(side="left", padx=8)

        # IBM credentials (hidden unless IBM mode)
        self.ibm_frame = ttk.Frame(settings)
        cred_note = ttk.Label(
            self.ibm_frame,
            text="Leave these blank if you've already saved your IBM "
                 "credentials on this computer before.",
            foreground="#777777",
        )
        cred_note.grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(2, 4))

        ttk.Label(self.ibm_frame, text="API key (token):").grid(row=1, column=0, sticky="e", padx=8, pady=2)
        self.token_entry = ttk.Entry(self.ibm_frame, width=52, show="*")
        self.token_entry.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(self.ibm_frame, text="Instance CRN:").grid(row=2, column=0, sticky="e", padx=8, pady=2)
        self.crn_entry = ttk.Entry(self.ibm_frame, width=52)
        self.crn_entry.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(self.ibm_frame, text="Backend (optional):").grid(row=3, column=0, sticky="e", padx=8, pady=2)
        self.backend_entry = ttk.Entry(self.ibm_frame, width=52)
        self.backend_entry.grid(row=3, column=1, sticky="w", pady=2)
        ttk.Label(
            self.ibm_frame,
            text="e.g. ibm_brisbane - leave blank to auto-pick the least busy device",
            foreground="#777777",
        ).grid(row=4, column=1, sticky="w", pady=(0, 4))

        # Numeric options
        opts_row = ttk.Frame(settings)
        opts_row.pack(fill="x", **pad)
        ttk.Label(opts_row, text="Optimization steps:").pack(side="left")
        self.iters_var = tk.IntVar(value=60)
        ttk.Spinbox(opts_row, from_=5, to=500, width=6, textvariable=self.iters_var).pack(side="left", padx=(4, 20))
        ttk.Label(opts_row, text="Shots (IBM mode):").pack(side="left")
        self.shots_var = tk.IntVar(value=10000)
        ttk.Spinbox(opts_row, from_=100, to=100000, increment=100, width=8,
                    textvariable=self.shots_var).pack(side="left", padx=4)

        hint = ttk.Label(
            settings,
            text="More steps = more accurate but slower. On real hardware every "
                 "step costs quota, so start small (e.g. 10-15 steps).",
            foreground="#777777",
        )
        hint.pack(anchor="w", padx=8, pady=(0, 6))

        # --- Buttons ---
        btn_row = ttk.Frame(self.root)
        btn_row.pack(fill="x", padx=12, pady=6)
        self.run_btn = ttk.Button(btn_row, text="▶  Run experiment", command=self.start_run)
        self.run_btn.pack(side="left")
        self.plot_btn = ttk.Button(btn_row, text="Show plots (incl. 3D)", command=self.show_plot, state="disabled")
        self.plot_btn.pack(side="left", padx=8)

        # --- Log output ---
        log_frame = ttk.LabelFrame(self.root, text="Progress")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self.log_box = scrolledtext.ScrolledText(log_frame, height=18, state="disabled",
                                                 font=("Courier", 10))
        self.log_box.pack(fill="both", expand=True, padx=4, pady=4)

        self._on_mode_change()

    def _on_mode_change(self):
        if self.mode_var.get() == "ibm":
            self.ibm_frame.pack(fill="x", padx=4, pady=2)
        else:
            self.ibm_frame.pack_forget()

    # ------------------------------------------------------------------
    # Logging (thread-safe via queue)
    # ------------------------------------------------------------------
    def log(self, message):
        self.log_queue.put(str(message))

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                self.log_box.insert("end", msg + "\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log_queue)

    # ------------------------------------------------------------------
    # Running the experiment
    # ------------------------------------------------------------------
    def start_run(self):
        if self.running:
            return
        mode = self.mode_var.get()
        if mode == "ibm":
            ok = messagebox.askyesno(
                "Run on real hardware?",
                "This will send jobs to a real IBM quantum computer and use "
                "your account quota. Depending on the queue, it can take a "
                "while. Continue?",
            )
            if not ok:
                return

        self.running = True
        self.results = None
        self.run_btn.configure(state="disabled", text="Running...")
        self.plot_btn.configure(state="disabled")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        thread = threading.Thread(target=self._run_worker, daemon=True)
        thread.start()

    def _run_worker(self):
        mode = self.mode_var.get()
        try:
            results = run_full_experiment(
                mode=mode,
                maxiter=int(self.iters_var.get()),
                shots=int(self.shots_var.get()),
                token=self.token_entry.get().strip() or None,
                instance=self.crn_entry.get().strip() or None,
                backend_name=self.backend_entry.get().strip() or None,
                log=self.log,
            )
            self.results = results
            self.log("")
            self.log("Done! Click 'Show plots (incl. 3D)' to see the "
                     "convergence, a 3D energy landscape, and IBM-style "
                     "3D quantum-state plots.")
        except Exception as exc:
            self.log("")
            self.log(f"ERROR: {exc}")
            if mode == "ibm":
                self.log("Tip: check your API key / instance CRN, and that "
                         "your account has hardware access.")
        finally:
            self.running = False
            self.root.after(0, self._run_finished)

    def _run_finished(self):
        self.run_btn.configure(state="normal", text="▶  Run experiment")
        if self.results is not None:
            self.plot_btn.configure(state="normal")

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------
    def show_plot(self):
        if not self.results:
            return
        import matplotlib.pyplot as plt

        r = self.results

        # --- Dashboard: 2D convergence + a 3D energy landscape ---
        fig = plt.figure(figsize=(15, 4.8))

        ax1 = fig.add_subplot(1, 3, 1)
        ax1.plot(r["history_h"], label="VQE energy", color="tab:blue")
        ax1.axhline(r["exact_h"], color="tab:red", linestyle="--", label="Exact")
        ax1.set_title("Hydrogen atom")
        ax1.set_xlabel("Iteration")
        ax1.set_ylabel("Energy (hartree)")
        ax1.legend()

        ax2 = fig.add_subplot(1, 3, 2)
        ax2.plot(r["history_h2"], label="VQE energy", color="tab:blue")
        ax2.axhline(r["exact_h2"], color="tab:red", linestyle="--", label="Exact")
        ax2.set_title("H₂ molecule")
        ax2.set_xlabel("Iteration")
        ax2.legend()

        try:
            gx, gy, gz, opt, labels = hydrogen_atom_energy_surface(r["params_h"])
            ax3 = fig.add_subplot(1, 3, 3, projection="3d")
            surf = ax3.plot_surface(gx, gy, gz, cmap="viridis", alpha=0.9,
                                    linewidth=0, antialiased=True)
            ax3.scatter([opt[0]], [opt[1]], [opt[2]], color="red", s=90,
                        depthshade=False, label="VQE minimum")
            ax3.set_title("H atom energy landscape (3D)")
            ax3.set_xlabel(labels[0])
            ax3.set_ylabel(labels[1])
            ax3.set_zlabel("Energy (hartree)")
            fig.colorbar(surf, ax=ax3, shrink=0.55, aspect=12, pad=0.12)
            ax3.legend(loc="upper right")
        except Exception as exc:
            self.log(f"(Could not draw 3D energy landscape: {exc})")

        fig.suptitle(
            f"Reaction energy H + H → H₂:  "
            f"exact {r['reaction_exact']:.4f}  |  VQE {r['reaction_vqe']:.4f} hartree"
        )
        fig.tight_layout()

        # --- IBM-style 3D quantum-state plots ---
        try:
            from qiskit.visualization import plot_state_city, plot_bloch_multivector

            sv_h = final_statevector("h", r["params_h"])
            sv_h2 = final_statevector("h2", r["params_h2"])

            plot_state_city(
                sv_h, title="H atom final state - density matrix (3D)")
            plot_state_city(
                sv_h2, title="H₂ final state - density matrix (3D)")
            plot_bloch_multivector(
                sv_h2, title="H₂ qubits on the Bloch sphere")
        except Exception as exc:
            self.log(f"(Could not draw quantum-state 3D plots: {exc})")

        plt.show()


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    VQEApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
