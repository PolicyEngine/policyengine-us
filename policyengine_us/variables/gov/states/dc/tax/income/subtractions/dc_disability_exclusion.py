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

        disability_payment = person("total_disability_payments", period)
        excludable_income = min_(disability_payment, p.cap)
        total_excludable_income = tax_unit.sum(excludable_income)

        federal_agi = tax_unit("adjusted_gross_income", period)
        social_security_income = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        income_after_reduction = max_(
            federal_agi - social_security_income - p.amount, 0
        )

        return total_excludable_income - income_after_reduction
