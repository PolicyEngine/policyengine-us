def test_microsim_runs_cps():
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    sim.calc("spm_unit_net_income")
