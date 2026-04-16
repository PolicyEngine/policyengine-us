from policyengine_us.model_api import *


class me_affordability_payment_subtraction_reported(Variable):
    value_type = float
    entity = TaxUnit
    label = "Reported Maine affordability payment subtraction"
    unit = USD
    documentation = (
        "Amount of the Maine affordability payment received in the tax year and "
        "included in federal AGI."
    )
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=2&snum=132#page=159"
    definition_period = YEAR
    defined_for = StateCode.ME
    default_value = 0
