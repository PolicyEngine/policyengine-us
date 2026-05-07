from policyengine_us.model_api import *


class ks_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
    )
    defined_for = "ks_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-100 and KEESM 7110:
        # Benefit = Payment Standard - Countable Income
        maximum_benefit = spm_unit("ks_tanf_maximum_benefit", period)
        countable_income = spm_unit("ks_tanf_countable_income", period)
        benefit = max_(maximum_benefit - countable_income, 0)
        return min_(benefit, maximum_benefit)
