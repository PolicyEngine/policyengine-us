from policyengine_us.model_api import *


class snap_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP income deductions"
    unit = USD
    documentation = "Deductions made from gross income for SNAP benefits"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.income.deductions
        total_deductions = add(spm_unit, period, p.allowed)
        proration_factor = spm_unit("snap_proration_factor", period)
        return total_deductions * proration_factor
