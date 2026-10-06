from policyengine_us.model_api import *


class investment_in_529_plan(Variable):
    value_type = float
    entity = TaxUnit
    label = "529 plan investment"
    unit = USD
    documentation = (
        "Amount the head and spouse contributed to 529 savings plans during "
        "the year. A dependent's own contributions are left out: the "
        "contributor deducts them, on their own return."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("investment_in_529_plan_indv", tax_unit, period)
