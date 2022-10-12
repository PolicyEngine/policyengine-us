from policyengine_us.model_api import *


class or_income_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR income subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=13",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.800
    )
    defined_for = StateCode.OR

    formula = sum_of_variables(
        "gov.states.or.tax.income.subtractions.subtractions"
    )
