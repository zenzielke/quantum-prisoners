# Quantum Prisoner's Dilemma Simulator

An interactive research tool exploring the **Eisert–Wilkens–Lewenstein (EWL) Protocol** for Quantum Game Theory. This project demonstrates how quantum entanglement can optimize collective outcomes from the classical Prisoner's Dilemma, shifting the Nash Equilibrium from mutual defection to mutual cooperation.


## Overview
In classical Game Theory, rational agents inevitably defect within the Prisoner's Dilemma. By "quantizing" the strategy space, we introduce an entanglement parameter ($\gamma$). This simulation proves that through entanglement ($\gamma = \pi/2$), a new "Quantum" strategy ($Q$) emerges that dominates the game.

**Key Features:**
- **Interactive Arena:** Play strategies ($C, D, Q$) against each other.
- **Entanglement Slider:** Vizualize the phase transition from Classical ($\gamma=0$) to Quantum ($\gamma=1.57$).
- **Circuit Visualization:** Dynamic rendering of the Qiskit quantum circuit.
- **Research Verification:** One-click reproduction of the payoff curves.

## Installation

1. **Clone the repository**
   bash
   git clone [https://github.com/zenzielke/quantum-prisoners.git](https://github.com/zenzielke/quantum-prisoners.git)
   cd quantum-prisoners


2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
## Usage

**To Run the Web App:**
   ```
   streamlist run app.py
   ```

**To Run just the Simulation:**
   ```
   python quantum_sim.py
   ```

## Stack
- **Qiskit:** Quantum circuit simulation.
- **Matplotlib/Numpy:** Data plotting and processing.
- **Streamlit:** Web visualization.

## License

This project is open-source.
