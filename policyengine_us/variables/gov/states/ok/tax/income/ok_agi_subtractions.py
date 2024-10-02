from policyengine_us.model_api import *


class ok_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf#page=16"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=16"
    )
    defined_for = StateCode.OK

    adds = "gov.states.ok.tax.income.agi.subtractions.subtractions"
