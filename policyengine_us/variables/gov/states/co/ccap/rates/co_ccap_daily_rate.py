from policyengine_us.model_api import *


class co_ccap_daily_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = (
        "Colorado Child Care Assistance Program daily rate for the child's care unit"
    )
    defined_for = StateCode.CO
    reference = (
        # 8 CCR 1403-1 3.130(C), PDF page 119.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=119",
        # Each county rate plan lists the PT, FTPT and FTFT rates CHATS pays.
        "https://drive.google.com/drive/folders/1YSLL5Sn32NyKbp8Z0063ldFbAhQwfHW_",
    )

    def formula(person, period, parameters):
        full_time_rate = person("co_ccap_full_time_daily_rate", period)
        unit = person("co_ccap_care_unit", period)
        # The county rate plans round each unit's rate half up to the cent: a
        # $60.90 full-time rate pays $33.50 part time (60.90 x 0.55 = 33.495).
        # Working in whole cents keeps the halves exact.
        cents = np.round(full_time_rate * 100) * np.round(unit * 100) / 100
        return np.floor(cents + 0.5) / 100
