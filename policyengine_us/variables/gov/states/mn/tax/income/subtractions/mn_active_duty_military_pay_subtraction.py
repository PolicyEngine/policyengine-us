from policyengine_us.model_api import *


class mn_active_duty_military_pay_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Active Duty Military Pay Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.20",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1m-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Minnesota residents in the armed forces can subtract
        # federal active-duty military pay included in federal AGI
        # This covers:
        # - Line 20: Federal active-duty military pay for MN residents
        # - Line 21: National Guard members and Reservists pay
        #   (training, state active service, AGR duty, etc.)
        # Note: Per M1M instructions, if income is included on Line 20,
        # it should not also be included on Line 21 (no double counting)
        # The military_service_income variable covers both active duty
        # and National Guard/Reserve pay.
        military_income = add(tax_unit, period, ["military_service_income"])
        return military_income
