from policyengine_us.model_api import *


class child_care_subsidies_above_provider_bills(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care subsidies above each provider's bill"
    documentation = (
        "The part of child care subsidy payments that exceeds the bill of the "
        "provider each payment goes to. That provider keeps it, and it pays "
        "none of another provider's bill. Zero for a program modeled with one "
        "payment against the whole family's bill."
    )
    unit = USD
    adds = ["vt_ccfap_payment_above_bill"]
