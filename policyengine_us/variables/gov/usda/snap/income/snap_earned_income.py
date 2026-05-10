from policyengine_us.model_api import *


class snap_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP earned income"
    documentation = (
        "Earned income for calculating the SNAP benefit. Reduced by "
        "the non-counted share of prorated-disqualified members' "
        "earned income per 7 CFR 273.11(c)(2) or (c)(3)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_1",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        raw = add(spm_unit, period, ["snap_earned_income_person"])
        reduction = spm_unit("snap_prorated_earned_income_reduction", period)
        return max_(raw - reduction, 0)
