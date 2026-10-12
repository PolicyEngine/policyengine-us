from policyengine_us.model_api import *


class or_ssp_available_room_board_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon income available for special room and board payments"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0630.pdf",
    )
    documentation = "Override with accessible income remaining after an assessed care liability during a certified absence, or accessible income in an approved incapacity case."

    def formula(person, period, parameters):
        return person("or_ssp_countable_income", period)
