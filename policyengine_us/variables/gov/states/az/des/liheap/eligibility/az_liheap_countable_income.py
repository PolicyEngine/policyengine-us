from policyengine_us.model_api import *


class az_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona LIHEAP countable income"
    definition_period = YEAR
    defined_for = StateCode.AZ
    unit = USD
    reference = "https://des.az.gov/services/basic-needs/liheap"
    documentation = "LIHEAP uses gross income for eligibility determination"

    def formula(spm_unit, period, parameters):
        # LIHEAP typically counts all gross income sources
        # Including employment, self-employment, social security, pensions, etc.
        income_sources = [
            "employment_income",
            "self_employment_income",
            "social_security",
            "pension_income",
            "unemployment_compensation",
            "ssi",
            "tanf",
            "interest_income",
            "dividend_income",
            "rental_income",
        ]
        
        return add(spm_unit, period, income_sources)