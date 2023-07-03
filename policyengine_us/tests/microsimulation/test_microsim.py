def test_microsim_runs_cps():
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    hnet = sim.calc("household_net_income")
    assert not hnet.isna().any(), "Some households have NaN net income."
    hidecile = sim.calc("household_income_decile")
    assert (hidecile >= 0 & hidecile <= 10).all()
    sidecile = sim.calc("spm_unit_income_decile")
    assert (sidecile >= 0 & sidecile <= 10).all()
