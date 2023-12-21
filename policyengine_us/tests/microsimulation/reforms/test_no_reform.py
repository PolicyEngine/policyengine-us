def test_no_reform_has_no_change():
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant
    import pandas as pd

    def modify_parameters(parameters):
        parameters.gov.usda.snap.income.deductions.earned_income.update(
            start=instant("2023-01-01"),
            stop=instant("2028-12-31"),
            value=0.20000001,
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    baseline = Microsimulation()
    reformed = Microsimulation(reform=reform)

    gain = reformed.calculate("household_net_income") - baseline.calculate(
        "household_net_income"
    )
    assert (gain.abs() > 1).mean() < 0.001
