from policyengine_us.model_api import *


class ia_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF gross income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Test 1: Gross income <= 185% of Standard of Need
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        gross_income_limit = spm_unit("ia_tanf_gross_income_limit", period)
        return gross_income <= gross_income_limit
