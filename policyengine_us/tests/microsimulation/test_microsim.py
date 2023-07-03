def test_microsim_runs_cps():
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    hnet = sim.calc("household_net_income")
    assert not hnet.isna().any(), "Some households have NaN net income."
    hidecile = sim.calc("household_income_decile")
    sidecile = sim.calc("spm_unit_income_decile")
