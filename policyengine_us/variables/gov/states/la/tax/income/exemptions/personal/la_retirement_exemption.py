from policyengine_us.model_api import *


class la_retirement_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana retirement exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pension_income = person("taxable_pension_income", period)
        age = person("age", period)
        p = parameters(period).gov.states.la.tax.income.exemptions.retirement
        cap = p.calc(age)
        deductible_pensions = min_(pension_income, cap)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(deductible_pensions * is_head_or_spouse)
