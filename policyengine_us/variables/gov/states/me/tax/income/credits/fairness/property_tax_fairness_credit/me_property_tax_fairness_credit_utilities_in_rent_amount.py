from policyengine_us.model_api import *


class me_property_tax_fairness_credit_utilities_in_rent_amount(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Amount of heat, utilities, furniture, or similar items included in rent for the Maine property tax fairness credit (0 = amount unknown, triggering the 15%-of-rent line 5c estimate)"
    documentation = (
        "Schedule PTFC/STFC line 5c: the dollar amount of heat, utilities, "
        "furniture, or similar items included in rent paid. A value of 0 is a "
        "sentinel meaning the amount is unknown (not that $0 of utilities were "
        "included); on that branch the credit uses the 15%-of-rent line 5c "
        "estimate instead of a known dollar amount."
    )
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_pstfc_ff.pdf#page=2"
