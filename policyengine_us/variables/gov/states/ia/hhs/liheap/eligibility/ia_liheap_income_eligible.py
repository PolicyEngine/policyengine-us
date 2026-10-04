from policyengine_us.model_api import *


class ia_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP income eligible"
    documentation = (
        "Annual countable household income is at or below the income limit. "
        "Section 5.10 ties financial eligibility to income 'being 200% or "
        "below' of the federal poverty guidelines, and the payment matrix makes "
        "only income 'Over 200%' ineligible, so income exactly at the limit "
        "qualifies."
    )
    reference = (
        # Section 5.10 (page 18) and Appendix I (page 137).
        "https://hhs.iowa.gov/media/17262/download?inline#page=18",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        income = spm_unit("ia_liheap_countable_income", period)
        limit = spm_unit("ia_liheap_income_limit", period)
        return income <= limit
