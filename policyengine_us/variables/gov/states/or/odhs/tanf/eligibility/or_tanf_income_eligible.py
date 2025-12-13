from policyengine_us.model_api import *


class or_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Oregon TANF income eligible"
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-160-0100"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        # Standard test: countable < limit AND adjusted < limit
        passes_countable_test = spm_unit(
            "or_tanf_countable_income_eligible", period
        )
        passes_adjusted_test = spm_unit(
            "or_tanf_adjusted_income_eligible", period
        )
        passes_standard_test = passes_countable_test & passes_adjusted_test

        # ELI test: countable < (payment_standard * multiplier)
        passes_eli_test = spm_unit("or_tanf_eli_income_eligible", period)

        eli_eligible = spm_unit("or_tanf_eli_eligible", period)
        return where(eli_eligible, passes_eli_test, passes_standard_test)
