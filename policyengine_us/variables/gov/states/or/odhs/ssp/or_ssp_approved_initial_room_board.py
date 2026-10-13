from policyengine_us.model_api import *


class or_ssp_approved_initial_room_board(Variable):
    value_type = float
    entity = Person
    label = "Oregon approved initial placement room and board payment"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0630.pdf#page=1",
    )
    documentation = "Approved payment for the covered initial placement period after the state assesses the unmet need; zero unless provided."
