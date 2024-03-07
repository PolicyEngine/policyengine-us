from policyengine_us.model_api import *


class dc_disability_exclusion(Variable):
    value_type = float
    entity = Person
    label = "DC disability exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.income.subtractions.disability_income_exclusion
        tax_unit = person.tax_unit

        disability_payments = person("total_disability_payments", period)
        capped_disability_payments = min_(disability_payments, p.cap)
        total_excludable_income = tax_unit.sum(capped_disability_payments)

        federal_agi = tax_unit("adjusted_gross_income", period)
        social_security_income = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        reduced_income = max_(
            federal_agi - social_security_income - p.amount, 0
        )

        return max_(total_excludable_income - reduced_income, 0)
