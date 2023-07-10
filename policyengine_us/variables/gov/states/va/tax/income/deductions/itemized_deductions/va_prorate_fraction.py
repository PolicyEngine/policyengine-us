from policyengine_us.model_api import *


class va_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Virginia joint amount proration fraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/","§ 58.1-322.03.(1.a.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18"
    )
    defined_for = StateCode.VA

    # get proportion of each person's share in the combined federal adjusted gross income.
    def formula(person, period, parameters):
        net_income = person("ia_net_income", period)
        total_net_income = person.tax_unit.sum(net_income)
        # If no net income, then assign entirely to head.
        return where(
            total_net_income == 0,
            person("is_tax_unit_head", period),
            net_income / total_net_income,
        )
