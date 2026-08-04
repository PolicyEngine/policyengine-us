from policyengine_us.model_api import *


class va_military_basic_pay_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia military basic pay subtraction for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.military_basic_pay
        military_pay = person("military_basic_pay", period)
        # Phases in then out dollar for dollar with respect to military pay.
        subtractable = where(
            military_pay < p.threshold,
            military_pay,
            max_(0, (2 * p.threshold) - military_pay),
        )
        return subtractable * person("is_tax_unit_head_or_spouse", period)
