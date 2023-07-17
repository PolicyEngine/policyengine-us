from policyengine_us.model_api import *


class de_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware refundable EITC"
    unit = USD
    documentation = (
        "Refundable EITC credit reducing DE State income tax page 8."
    )
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = "de_claims_refundable_eitc"

    adds = ["de_refundable_eitc_if_claimed"]
