from policyengine_us.model_api import *


class or_federal_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Federal Pension Subtraction"
    unit = USD
    definition_period = YEAR
    default_value = 0.0
    documentation = (
        "Subtraction for federal pension income attributable to federal service "
        "occurring before October 1, 1991, under ORS 316.680(1)(e) (Schedule OR-ASC code 307)."
    )
    reference = (
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2022.pdf#page=74",
    )
    defined_for = StateCode.OR
