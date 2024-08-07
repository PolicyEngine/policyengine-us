def test_repeal_head_of_household():
    import numpy as np
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant

    class neutralize_reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    baseline = Microsimulation()
    neutralize_reformed = Microsimulation(reform=neutralize_reform)

    baseline_netincome = baseline.calculate("household_net_income")
    neutralize_reform_netincome = neutralize_reformed.calculate(
        "household_net_income"
    )

    # Check the same result using the reform.

    def modify_parameters(parameters):
        parameters.gov.contrib.congress.romney.family_security_act.remove_head_of_household.update(
            start=instant("2023-01-01"),
            stop=instant("2028-12-31"),
            value=True,
        )
        return parameters

    class parameter_reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    parameter_reformed = Microsimulation(reform=parameter_reform)
    parameter_reform_netincome = parameter_reformed.calculate(
        "household_net_income"
    )

    bni_is_nan = np.isnan(baseline_netincome)
    print('baseline   NaN count', bni_is_nan.sum())
    nni_is_nan = np.isnan(neutralize_reform_netincome)
    print('neutralize NaN count', nni_is_nan.sum())
    pni_is_nan = np.isnan(parameter_reform_netincome)
    print('parameter  NaN count', pni_is_nan.sum())

    # Check they're the same, element by element.
    assert np.allclose(neutralize_reform_netincome, parameter_reform_netincome)

    # Check they're the right order of magnitude.
    total_loss = (baseline_netincome - neutralize_reform_netincome).sum()
    # CBO estimates $10B to $20B:
    # https://www.cbo.gov/budget-options/54789
    assert total_loss > 5e9
    assert total_loss < 25e9
