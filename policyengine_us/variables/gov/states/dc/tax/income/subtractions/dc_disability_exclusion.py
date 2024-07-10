from policyengine_us.model_api import *


class dc_disability_exclusion(Variable):
    value_type = float
    entity = Person
    label = "DC disability exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.02#(a)(2)(M)"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.disability_income_exclusion
        tax_unit = person.tax_unit

        disability_payments = person("total_disability_payments", period)
        capped_disability_payments = min_(disability_payments, p.cap)
        total_capped_payments = tax_unit.sum(capped_disability_payments)

        federal_agi = tax_unit("adjusted_gross_income", period)
        social_security_income = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        reduced_income = federal_agi - social_security_income - p.amount
        capped_reduced_income = max_(reduced_income, 0)

        return max_(total_capped_payments - capped_reduced_income, 0)
