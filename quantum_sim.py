import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Operator
from scipy.linalg import expm

PAYOFFS = {
    '00': 3,
    '01': 5,
    '10': 0,
    '11': 1
}

I = np.array([[1, 0], 
              [0, 1]])

D = np.array([[0, 1j], 
              [1j, 0]])

Q = np.array([[1j, 0], 
              [0, -1j]])

def get_strategy_operator(label):
    if label == 'C': return Operator(I)
    if label == 'D': return Operator(D)
    if label == 'Q': return Operator(Q)
    raise ValueError(f"Unknown strategy: {label}")

def get_J_gate(gamma):

    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    
    # Calculate matrix exponential
    J_matrix = expm(1j * gamma * XX / 2)
    return Operator(J_matrix)

def run_ewl_circuit(strat_A, strat_B, gamma, shots=4096):

    qc = QuantumCircuit(2, 2)
    
    J = get_J_gate(gamma)
    qc.append(J, [0, 1])
    qc.barrier()
    
    op_A = get_strategy_operator(strat_A)
    op_B = get_strategy_operator(strat_B)
    
    qc.append(op_A, [0])
    qc.append(op_B, [1])
    qc.barrier()
    
    J_dag = J.adjoint()
    qc.append(J_dag, [0, 1])
    
    qc.measure([0, 1], [0, 1])
    
    sim = AerSimulator()
    job = sim.run(transpile(qc, sim), shots=shots)
    counts = job.result().get_counts()
    
    return counts

def get_expected_payoff(counts, shots):
    total_score = 0
    for outcome, count in counts.items():

        bin_alice = outcome[1]
        bin_bob = outcome[0]

        key = bin_bob + bin_alice


        score = PAYOFFS[key]
        total_score += score * count
        
    return total_score / shots

def experiment_1_entanglement_sweep():
    print("\nRunning Experiment 1: The Effect of Gamma (RQ1)...")
    gammas = np.linspace(0, np.pi/2, 25)
    
    payoffs_classical = []
    payoffs_quantum = []
    
    for g in gammas:
        c_dd = run_ewl_circuit('D', 'D', g)
        payoffs_classical.append(get_expected_payoff(c_dd, 4096))
        
        c_qd = run_ewl_circuit('Q', 'D', g)
        payoffs_quantum.append(get_expected_payoff(c_qd, 4096))
        
    plt.figure(figsize=(10,6))
    plt.plot(gammas, payoffs_classical, 'r--', label='D vs D (Classical)')
    plt.plot(gammas, payoffs_quantum, 'b-', linewidth=2, label='Q vs D (Quantum)')
    
    plt.title("Transition from Classical to Quantum")
    plt.xlabel(r"Entanglement Parameter $\gamma$")
    plt.ylabel("Alice's Expected Payoff")
    plt.axvline(x=0, color='gray', linestyle=':', label='Separable')
    plt.axvline(x=1.57, color='green', linestyle=':', label='Max Entanglement')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    filename = "rq1_entanglement_plot.png"
    plt.savefig(filename)
    print(f"Graph saved to {filename}")

def experiment_2_equilibrium_check():
    print("\nRunning Experiment 2: Equilibrium Analysis (RQ2)...")
    print("Simulating full game at Max Entanglement (Gamma = Pi/2)")
    
    strategies = ['C', 'D', 'Q']
    gamma_max = np.pi/2
    
    print("-" * 50)
    print(f"{'Alice \\ Bob':<12} | {'C':^8} | {'D':^8} | {'Q':^8} |")
    print("-" * 50)
    
    for sA in strategies:
        row_string = f" {sA:<11} |"
        for sB in strategies:
            counts = run_ewl_circuit(sA, sB, gamma_max)
            payoff = get_expected_payoff(counts, 4096)
            row_string += f" {payoff:^8.1f} |"
        print(row_string)
    print("-" * 50)

if __name__ == "__main__":
    experiment_1_entanglement_sweep()
    experiment_2_equilibrium_check()