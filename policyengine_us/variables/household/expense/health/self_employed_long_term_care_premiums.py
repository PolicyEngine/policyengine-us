from policyengine_us.model_api import *


class self_employed_long_term_care_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed long-term care insurance premiums"
    unit = USD
    documentation = (
        "Eligible long-term care premiums that count toward the self-employed "
        "health insurance deduction (Form 7206 line 2). 26 U.S.C. "
        "162(l)(2)(C) takes in a qualified long-term care insurance contract "
        "only up to the 26 U.S.C. 213(d)(10) limit for each person covered. "
        "long_term_health_insurance_premiums is recorded on the insured "
        "person, and the model treats that person as the payer, so a "
        "self-employed person's deduction takes in that person's own contract."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_C",
        "https://www.irs.gov/pub/irs-prior/f7206--2024.pdf#page=1",  # Line 2
    )
    defined_for = "is_self_employed"
    adds = ["eligible_long_term_care_premiums"]
