from policyengine_us.model_api import *


class va_military_basic_pay_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Virginia personal exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.military_basic_pay
        # TODO: Sum for head and spouse - not just everyone in tax unit.
        # Use is_tax_unit_head and is_tax_unit_spouse
        military_pay = person("military_pay", period)
        return where(military_pay < p.threshold, military_pay, max_(0, (2 * p.threshold) - military_pay))
