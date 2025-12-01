import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Operator
from scipy.linalg import expm

PAYOFFS = {
    '00': (3, 3),
    '01': (5, 0),
    '10': (0, 5),
    '11': (1, 1)
}

I = np.array([[1, 0], [0, 1]])
D = np.array([[0, 1j], [1j, 0]])
Q = np.array([[1j, 0], [0, -1j]])

def get_strategy_operator(label):
    if 'Cooperate' in label: return Operator(I)
    if 'Defect' in label: return Operator(D)
    if 'Quantum' in label: return Operator(Q)
    return Operator(I)

def get_J_gate(gamma):
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    J_matrix = expm(1j * gamma * XX / 2)
    return Operator(J_matrix)

def run_circuit(strat_A, strat_B, gamma, shots):
    qc = QuantumCircuit(2, 2)
    qc.append(get_J_gate(gamma), [0, 1])
    qc.barrier()
    qc.append(get_strategy_operator(strat_A), [0])
    qc.append(get_strategy_operator(strat_B), [1])
    qc.barrier()
    qc.append(get_J_gate(gamma).adjoint(), [0, 1])
    qc.measure([0, 1], [0, 1])
    
    sim = AerSimulator()
    job = sim.run(transpile(qc, sim), shots=shots)
    return job.result().get_counts(), qc

def calculate_expected_payoff(counts, shots):
    alice_score = 0
    bob_score = 0
    for outcome, count in counts.items():
        # Qiskit Key is 'BobAlice' (q1q0)
        key = outcome[0] + outcome[1] 
        p_alice, p_bob = PAYOFFS[key]
        alice_score += p_alice * count
        bob_score += p_bob * count
    return alice_score/shots, bob_score/shots

st.set_page_config(page_title="Quantum Prisoner's Dilemma", layout="wide")

st.title("Quantum Prisoner's Dilemma")

# Initialize Session State to hold results
if 'counts' not in st.session_state:
    st.session_state['counts'] = None
if 'qc' not in st.session_state:
    st.session_state['qc'] = None
if 'payoffs' not in st.session_state:
    st.session_state['payoffs'] = (0, 0)

# --- SIDEBAR ---
st.sidebar.header("Game Settings")
gamma_input = st.sidebar.slider(
    r"Entanglement Parameter ($\gamma$)", 
    0.0, 1.57, 0.0, 0.01,
    help="0 = Classical, 1.57 = Max Quantum"
)
st.sidebar.subheader("Strategies")
strat_alice = st.sidebar.selectbox("Alice", ['Cooperate (C)', 'Defect (D)', 'Quantum (Q)'], index=1)
strat_bob = st.sidebar.selectbox("Bob", ['Cooperate (C)', 'Defect (D)', 'Quantum (Q)'], index=1)
shots = st.sidebar.number_input("Shots", value=4096)

# --- TABS ---
tab1, tab2 = st.tabs(["Simulation", "Visual"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info(f"**Matchup:** {strat_alice} vs {strat_bob}")
        
        if st.button("Run Simulation", type="primary"):
            # Run and save to session state
            c, q = run_circuit(strat_alice, strat_bob, gamma_input, shots)
            p_a, p_b = calculate_expected_payoff(c, shots)
            st.session_state['counts'] = c
            st.session_state['qc'] = q
            st.session_state['payoffs'] = (p_a, p_b)

        # Display Results if they exist
        if st.session_state['counts'] is not None:
            pa, pb = st.session_state['payoffs']
            sc1, sc2 = st.columns(2)
            sc1.metric("Alice", f"{pa:.2f}")
            sc2.metric("Bob", f"{pb:.2f}")
            
            if pa > pb: st.success("Alice Wins!")
            elif pb > pa: st.error("Bob Wins!")
            else: st.warning("Equilibrium / Tie")
            
            st.bar_chart(st.session_state['counts'])

    with col2:
        st.subheader("Quantum Circuit")
        # Only draw if a circuit exists
        if st.session_state['qc'] is not None:
            fig, ax = plt.subplots()
            st.session_state['qc'].draw(output='mpl', ax=ax)
            st.pyplot(fig)
        else:
            st.write("Run the simulation to generate the circuit.")

with tab2:
    st.header("Produce Graphs")
    if st.button("Generate Entanglement Plot"):
        with st.spinner("Simulating full sweep..."):
            gammas = np.linspace(0, 1.57, 20)
            payoffs_d, payoffs_q = [], []
            
            # Progress bar
            bar = st.progress(0)
            for idx, g in enumerate(gammas):
                # D vs D
                c1, _ = run_circuit('Defect', 'Defect', g, 1024)
                p1, _ = calculate_expected_payoff(c1, 1024)
                payoffs_d.append(p1)
                
                # Q vs D
                c2, _ = run_circuit('Quantum', 'Defect', g, 1024)
                p2, _ = calculate_expected_payoff(c2, 1024)
                payoffs_q.append(p2)
                bar.progress((idx+1)/20)
                
            fig2, ax2 = plt.subplots()
            ax2.plot(gammas, payoffs_d, 'r--', label='Classical (D vs D)')
            ax2.plot(gammas, payoffs_q, 'b-', linewidth=2, label='Quantum (Q vs D)')
            ax2.set_xlabel("Entanglement")
            ax2.set_ylabel("Alice's Payoff")
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            st.pyplot(fig2)
