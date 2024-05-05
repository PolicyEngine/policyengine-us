from policyengine_us.model_api import *


class la_retirement_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Louisiana retirement exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        pension_income = person("taxable_pension_income", period)
        age = person("age", period)
        p = parameters(
            period
        ).gov.states.la.tax.income.exempt_income.retirement
        cap = p.cap.calc(age)
        deductible_pensions = min_(pension_income, cap)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return deductible_pensions * is_head_or_spouse
