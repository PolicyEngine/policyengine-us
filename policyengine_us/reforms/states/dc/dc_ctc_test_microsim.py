def test_repeal_head_of_household():
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant
    from numpy.testing import assert_allclose

    class neutralize_reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    baseline = Microsimulation()
    neutralize_reformed = Microsimulation(reform=neutralize_reform)

    baseline_net_income = baseline.calculate("household_net_income")
    neutralize_reform_net_income = neutralize_reformed.calculate(
        "household_net_income"
    )

    # Check the same result using the reform.

    def modify_parameters(parameters):
        parameters.gov.contrib.states.dc.ctc.in_effect.update(
            start=instant("2023-01-01"),
            stop=instant("2028-12-31"),
            value=True,
        )
        return parameters

    class parameter_reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    dc_ctc_reformed = Microsimulation(reform=parameter_reform)
    dc_ctc_reform_net_income = dc_ctc_reformed.calculate(
        "household_net_income"
    )

    # Check they're the same, element by element.
    assert_allclose(neutralize_reform_net_income, dc_ctc_reform_net_income)

    # Check they're the right order of magnitude.
    total_loss = (baseline_net_income - neutralize_reform_net_income).sum()

    assert total_loss > 20e6
    assert total_loss < 100e6
