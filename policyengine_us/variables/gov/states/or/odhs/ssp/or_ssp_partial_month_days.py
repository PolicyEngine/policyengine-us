from policyengine_us.model_api import *


class or_ssp_partial_month_days(Variable):
    value_type = int
    entity = Person
    label = "Oregon SSP eligible days in a partial month"
    definition_period = MONTH
    defined_for = StateCode.OR
    reference = (
        "https://ch461rules.odhs.oregon.gov/rules/461-160-0070.pdf",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0700.pdf#page=3",
    )
    documentation = "Days of eligibility in a month of less than full eligibility. Leave at 0 for a full month. Enter it for the month, since a yearly value applies to every month. An approved initial room-and-board payment is already the amount for the covered period."
