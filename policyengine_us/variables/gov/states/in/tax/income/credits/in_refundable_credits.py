from policyengine_us.model_api import *


class in_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana refundable income tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1"
    defined_for = StateCode.IN
    # Use this instead of the parameter because the .in breaks the adds.
    # Use this instead of a formula so the app displays the breakdown.
    adds = ["in_eitc", "in_unified_elderly_tax_credit"]
