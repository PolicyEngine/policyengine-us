from policyengine_us.model_api import *


class me_affordability_payment_subtraction_reported(Variable):
    value_type = float
    entity = TaxUnit
    label = "Reported Maine affordability payment subtraction"
    unit = USD
    reference = "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=158"
    definition_period = YEAR
    defined_for = StateCode.ME
