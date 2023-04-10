from policyengine_us.model_api import *


class va_military_basic_pay_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia military basic pay subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.va.tax.income.subtractions.military_basic_pay
        # Compute subtractable military pay for head and spouse separately.
        military_pay = person("military_basic_pay", period)
        # Subtraction phases in and then out dollar for dollar with respect to military pay, at a given threshold.
        subtractable_military_pay = where(
            military_pay < p.threshold,
            military_pay,
            max_(0, (2 * p.threshold) - military_pay),
        )
        is_head_or_spouse = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        # Sum subtractable military pay for heads and spouses.
        return tax_unit.sum(subtractable_military_pay * is_head_or_spouse)
