from policyengine_us.model_api import *


class va_military_basic_pay_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Virginia military basic pay subtraction"
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
        head_military_pay = person("military_pay", "is_tax_unit_head", period)
        spouse_military_pay = person("military_pay", "is_tax_unit_spouse", period)
        military_pay_sum = sum(where(head_military_pay < p.threshold, head_military_pay, max_(0, (2 * p.threshold) - head_military_pay)),
                               where(spouse_military_pay < p.threshold, spouse_military_pay, max_(0, (2 * p.threshold) - spouse_military_pay)))
        return military_pay_sum
