from policyengine_us.model_api import *


def create_abolish_snap_net_income_test() -> Reform:
    class meets_snap_net_income_test(Variable):
        value_type = bool
        entity = SPMUnit
        label = "Meets SNAP net income test"
        documentation = "Whether this SPM unit meets the SNAP net income test"
        definition_period = MONTH
        reference = (
            "https://www.law.cornell.edu/uscode/text/7/2017#a",
            "https://www.law.cornell.edu/uscode/text/7/2014#c",
        )

        def formula(spm_unit, period, parameters):
            return True

    class reform(Reform):
        def apply(self):
            self.update_variable(meets_snap_net_income_test)

    return reform


def create_abolish_snap_net_income_test_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_abolish_snap_net_income_test()

    p = parameters(period).gov.contrib.snap.abolish_net_income_test

    if p.in_effect:
        return create_abolish_snap_net_income_test()
    else:
        return None


abolish_snap_net_income_test = create_abolish_snap_net_income_test_reform(
    None, None, bypass=True
)
