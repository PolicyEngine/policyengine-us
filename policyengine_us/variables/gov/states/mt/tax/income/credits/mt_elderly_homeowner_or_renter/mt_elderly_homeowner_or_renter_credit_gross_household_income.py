from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_gross_household_income(Variable):
    value_type = float
    entity = Person
    label = "Montana gross household income for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-23/section-15-30-2337/"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        sources = add(person, period, p.gross_income_sources)
        # AGI only captures the taxable portion of Social Security; add the
        # untaxed portion so all SS is counted per § 15-30-2337(9)(a)(viii).
        social_security = person("social_security", period)
        taxable_social_security = person("taxable_social_security", period)
        untaxed_social_security = max_(social_security - taxable_social_security, 0)
        return sources + untaxed_social_security
