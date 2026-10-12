from policyengine_us.model_api import *


class va_national_guard_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia national guard pay subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.national_guard_pay
        # Va. Code 58.1-322.02(8) subtracts "the wages or salaries received by
        # any person" for Guard service, up to the cap for each person. A tax
        # unit dependent's pay is on the dependent's own return.
        person = tax_unit.members
        head_or_spouse = ~person("is_tax_unit_dependent", period)
        pay = person("military_service_income", period) * head_or_spouse
        return tax_unit.sum(min_(pay, p.cap))
