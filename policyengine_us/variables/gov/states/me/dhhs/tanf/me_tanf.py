from policyengine_us.model_api import *


class me_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine TANF"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts",
    )
    defined_for = "me_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(8):
        # Benefit = min(Maximum Payment Level, Standard of Need - Countable Income)
        standard_of_need = spm_unit("me_tanf_standard_of_need", period)
        countable_income = spm_unit("me_tanf_countable_income", period)
        maximum_benefit = spm_unit("me_tanf_maximum_benefit", period)

        computed_benefit = max_(standard_of_need - countable_income, 0)
        # NOTE: Maine also provides a Special Need Housing Allowance (SNHA) of up
        # to $300/month for households with housing costs >= 50% of countable
        # income. SNHA is not modeled. See 10-144 C.M.R. Chapter 331, Section G(4).
        return min_(computed_benefit, maximum_benefit)
