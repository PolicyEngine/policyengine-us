from policyengine_us.model_api import *


class mn_military_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Military Pension Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.21",  # Subd. 21 - Military service pension; retirement pay
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1m-25.pdf",
    )
    defined_for = StateCode.MN
    adds = ["military_retirement_pay", "military_retirement_pay_survivors"]
