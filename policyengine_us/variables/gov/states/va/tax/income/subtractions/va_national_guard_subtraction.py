from policyengine_us.model_api import *


class va_national_guard_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia national guard pay subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.va.tax.income.subtractions

        return min_(
            tax_unit.sum(person("military_service_income", period)),
            p.national_guard_income,
        )
