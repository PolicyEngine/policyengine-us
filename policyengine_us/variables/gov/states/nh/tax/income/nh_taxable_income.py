from policyengine_us.model_api import *


class nh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.gencourt.state.nh.us/rsa/html/V/77/77-4.htm "
    defined_for = StateCode.NH
    adds = ["dividend_income", "interest_income"]
