from policyengine_us.model_api import *


class mn_active_duty_military_pay_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Active Duty Military Pay Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.12",  # Subd. 12 - Armed forces active duty compensation
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1m-25.pdf",
    )
    defined_for = StateCode.MN
    adds = ["military_service_income"]
