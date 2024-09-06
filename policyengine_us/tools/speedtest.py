from policyengine_us import Simulation, Microsimulation
from policyengine_core.tracers import FullTracer

simulation = Microsimulation()
simulation.trace = True
simulation.calculate("household_net_income", 2023)
simulation.tracer.generate_performance_graph(".")
