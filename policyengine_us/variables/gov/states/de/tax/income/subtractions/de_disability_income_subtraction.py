from policyengine_us.model_api import *


class de_disability_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware disability income subtraction"
    defined_for = StateCode.DE
    unit = USD
    definition_period = YEAR
    reference = (
        "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.disability_income
        # Subtraction phases in and then out dollar for dollar with respect to disability income, at a given threshold.
        subtractable_disability_income = min_(
            person("disability_benefits", period), p.amount
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = head | spouse
        return tax_unit.sum(subtractable_disability_income * is_head_or_spouse)
