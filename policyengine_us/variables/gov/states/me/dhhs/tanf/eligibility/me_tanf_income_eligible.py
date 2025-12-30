from policyengine_us.model_api import *


class me_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Maine TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://www.mainelegislature.org/legis/statutes/22/title22sec3762.html",
        "https://www.law.cornell.edu/regulations/maine/10-144-C-M-R-ch-331-app-Charts",
    )
    defined_for = StateCode.ME

    def formula(spm_unit, period, parameters):
        # Per 22 M.R.S. Section 3762(3)(B)(7-F):
        # Countable income must not exceed the Standard of Need
        countable_income = spm_unit("me_tanf_countable_income", period)
        standard_of_need = spm_unit("me_tanf_standard_of_need", period)
        return countable_income <= standard_of_need
