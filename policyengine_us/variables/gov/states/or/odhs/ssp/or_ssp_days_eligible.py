from policyengine_us.model_api import *


class or_ssp_days_eligible(Variable):
    value_type = int
    entity = Person
    label = "Days eligible for Oregon SSP this month"
    definition_period = MONTH
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-160-0070.pdf",
    )
    documentation = "Days for which the approved special need is payable. An approved initial room-and-board payment is already the amount for the covered period."

    def formula(person, period, parameters):
        return period.days
