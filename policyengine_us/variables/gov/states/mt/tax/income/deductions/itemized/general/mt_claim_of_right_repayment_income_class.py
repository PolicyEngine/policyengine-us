from policyengine_us.model_api import *


class mt_claim_of_right_repayment_income_class(Variable):
    value_type = int
    entity = Person
    label = "Income class of the Montana claim of right repayment"
    documentation = (
        "User-assigned class identifier for the person's claim of right "
        "repayment. Use the same identifier for head and spouse repayments "
        "of the same federal income class, and different identifiers for "
        "different classes. The default represents one common income class. "
        "Each person's repayment input represents the aggregate for that class. "
        "Used only to classify the historical Montana miscellaneous deduction; "
        "the federal section 1341 calculation retains its aggregate model."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-26/section-1.1341-1#p-1.1341-1(a)(3)"
    )
    defined_for = StateCode.MT
