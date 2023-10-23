from policyengine_us.model_api import *


class ar_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    # adds = "gov.states.ar.tax.income.credits.non_refundable"
    adds = [
        "ar_aged_credit",
        "ar_blind_credit",
        "ar_deaf_credit",
        "ar_dependent_credit",
        "ar_status_credit",
        "ar_personal_credit_aged_special",
    ]
