from policyengine_us.model_api import *


class ia_tanf_fip_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "Iowa HHS FIP Income Manual Chapter 4-E"
    documentation = "https://hhs.iowa.gov/media/3970"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # Unearned income includes benefits, interest, dividends, etc.
        # Exclude SSI as it's not counted per Iowa rules
        person = spm_unit.members

        # Get various unearned income sources
        unemployment = person("unemployment_compensation", period)
        social_security = person("social_security", period)
        veterans_benefits = person("veterans_benefits", period)
        disability_benefits = person("disability_benefits", period)
        interest = person("interest_income", period)
        dividend = person("dividend_income", period)

        total_unearned = (
            unemployment
            + social_security
            + veterans_benefits
            + disability_benefits
            + interest
            + dividend
        )

        return spm_unit.sum(total_unearned)
