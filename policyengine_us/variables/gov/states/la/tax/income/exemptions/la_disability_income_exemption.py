from policyengine_us.model_api import *


class la_disability_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana disability income exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"  # (B)
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        amount = parameters(
            period
        ).gov.states.la.tax.income.exemptions.disability_income
        disability_exemption = min_(
            person("disability_benefits", period), amount
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = head | spouse
        return tax_unit.sum(disability_exemption * is_head_or_spouse)
