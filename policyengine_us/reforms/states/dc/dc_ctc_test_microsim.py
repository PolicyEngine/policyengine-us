def test_dc_ctc():
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant

    baseline = Microsimulation()

    baseline_net_income = baseline.calculate(
        "household_net_income", period=2025
    )

    def modify_parameters(parameters):
        parameters.gov.contrib.states.dc.ctc.in_effect.update(
            start=instant("2025-01-01"),
            stop=instant("2028-12-31"),
            value=True,
        )
        return parameters

    class parameter_reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    dc_ctc_reformed = Microsimulation(reform=parameter_reform)
    dc_ctc_reform_net_income = dc_ctc_reformed.calculate(
        "household_net_income", period=2025
    )

    total_loss = (dc_ctc_reform_net_income - baseline_net_income).sum()

    assert total_loss > 5e6
    assert total_loss < 100e6
