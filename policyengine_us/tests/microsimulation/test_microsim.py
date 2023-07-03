def test_microsim_runs_cps():
    import numpy as np
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    hnet = sim.calc("household_net_income")
    assert not hnet.isna().any(), "Some households have NaN net income."
    hidecile = sim.calc("household_income_decile")
    assert np.all(hidecile >= 1) and np.all(hidecile <= 10)
    sidecile = sim.calc("spm_unit_income_decile")
    assert np.all(sidecile >= 1) and np.all(sidecile <= 10)
    idecile = sim.calc("income_decile")
    assert np.all(idecile >= 1) and np.all(idecile <= 10)
