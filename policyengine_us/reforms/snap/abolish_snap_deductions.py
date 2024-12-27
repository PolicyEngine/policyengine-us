from policyengine_us.model_api import *


def create_abolish_snap_deductions() -> Reform:
    class snap_deductions(Variable):
        value_type = float
        entity = SPMUnit
        label = "SNAP income deductions"
        unit = USD
        documentation = "Deductions made from gross income for SNAP benefits"
        definition_period = MONTH
        reference = "https://www.law.cornell.edu/uscode/text/7/2014#e"

        def formula(spm_unit, period, parameters):
            return 0

    class reform(Reform):
        def apply(self):
            self.update_variable(snap_deductions)

    return reform


def create_abolish_snap_deductions_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_abolish_snap_deductions()

    p = parameters(period).gov.contrib.snap.abolish_deductions

    if p.in_effect:
        return create_abolish_snap_deductions()
    else:
        return None


abolish_snap_deductions = create_abolish_snap_deductions_reform(
    None, None, bypass=True
)
