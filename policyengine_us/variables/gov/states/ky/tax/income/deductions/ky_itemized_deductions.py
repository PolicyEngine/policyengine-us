from policyengine_us.model_api import *


class ky_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "KY Itemized Deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf"
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    )
    defined_for = StateCode.KY
    adds = "gov.states.ky.tax.income.deductions.itemized"

    # Assume that married filing separate spouses each fill out their own Schedule A.
    # They are allowed to do this or file a joint Schedule A and divide by share of income.
