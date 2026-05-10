from policyengine_us.model_api import *


class snap_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP unearned income"
    documentation = (
        "Unearned income for calculating the SNAP benefit. Reduced by "
        "the non-counted share of prorated-disqualified members' "
        "Person-level unearned income per 7 CFR 273.11(c)(2) or "
        "(c)(3)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        raw = add(
            spm_unit,
            period,
            list(parameters(period).gov.usda.snap.income.sources.unearned),
        )
        reduction = spm_unit("snap_prorated_unearned_income_reduction", period)
        return max_(raw - reduction, 0)
