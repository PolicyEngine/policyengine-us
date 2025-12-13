from policyengine_us.model_api import *


class ga_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.sos.ga.gov/gac/290-2-28",
        "https://pamms.dhs.ga.gov/dfcs/tanf/",
    )
    defined_for = "ga_tanf_eligible"

    def formula(spm_unit, period, parameters):
        standard_of_need = spm_unit("ga_tanf_standard_of_need", period)
        countable_income = spm_unit("ga_tanf_countable_income", period)
        family_maximum = spm_unit("ga_tanf_family_maximum", period)

        # Benefit = MIN(Standard of Need - Countable Income, Family Maximum)
        benefit_before_max = max_(standard_of_need - countable_income, 0)
        return min_(benefit_before_max, family_maximum)
