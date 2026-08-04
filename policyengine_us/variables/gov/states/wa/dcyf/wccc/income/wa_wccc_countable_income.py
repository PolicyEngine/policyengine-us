from policyengine_us.model_api import *


class wa_wccc_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington WCCC countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0060",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0065",
    )

    adds = "gov.states.wa.dcyf.wccc.sources"
    subtracts = ["child_support_expense"]
