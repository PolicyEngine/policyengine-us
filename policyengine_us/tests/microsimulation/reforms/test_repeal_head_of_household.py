def test_no_reform_has_no_change():
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform

    class reform(Reform):
        def apply(self):
            self.neutralize_variable("head_of_household_eligible")

    baseline = Microsimulation()
    reformed = Microsimulation(reform=reform)

    gain = reformed.calculate("household_net_income") - baseline.calculate(
        "household_net_income"
    )
    total_loss = -gain.sum()
    # CBO estimates $10B to $20B:
    # https://www.cbo.gov/budget-options/54789
    assert total_loss > 5e9
    assert total_loss < 25e9
