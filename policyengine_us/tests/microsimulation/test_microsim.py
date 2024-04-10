def test_microsim_runs_cps():
    import numpy as np
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    hnet = sim.calc("household_net_income")
    assert not hnet.isna().any(), "Some households have NaN net income."
    # Deciles are 1-10, with -1 for negative income.
    hidecile = sim.calc("household_income_decile")
    assert np.all(hidecile >= -1) and np.all(hidecile <= 10)
    sidecile = sim.calc("spm_unit_income_decile")
    assert np.all(sidecile >= -1) and np.all(sidecile <= 10)
    idecile = sim.calc("income_decile")
    assert np.all(idecile >= -1) and np.all(idecile <= 10)
    # Check the sign of all the household net income components.
    assert np.all(sim.calc("household_tax_before_refundable_credits") >= 0)
    assert np.all(sim.calc("household_refundable_credits") >= 0)
    assert np.all(sim.calc("household_benefits") >= 0)
