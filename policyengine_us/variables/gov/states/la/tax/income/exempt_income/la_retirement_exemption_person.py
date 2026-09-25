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
        # Under La. R.S. 47:44.1, persons 65 or older may exempt up to $6,000 of annual
        # retirement income (Schedule E code 06E). Public retirement benefits (LASERS, TRSLA,
        # federal civil service) are fully exempt under Schedule E codes 02E/03E/05E via
        # sources.yaml and do not consume this exemption cap.
        pension_income = person("taxable_private_pension_income", period)
        age = person("age", period)
        p = parameters(period).gov.states.la.tax.income.exempt_income.retirement
        cap = p.cap.calc(age)
        deductible_pensions = min_(pension_income, cap)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return deductible_pensions * is_head_or_spouse
