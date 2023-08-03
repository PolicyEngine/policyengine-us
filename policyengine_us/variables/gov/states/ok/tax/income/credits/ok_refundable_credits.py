from policyengine_us.model_api import *


class ok_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK
    adds = "gov.states.ok.tax.income.credits.refundable"
