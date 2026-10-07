from policyengine_us.model_api import *


class second_residence_mortgage_points(Variable):
    value_type = float
    entity = Person
    label = "Deductible points paid on a second-residence mortgage"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "This year's deductible points on debt secured by the taxpayer's "
        "second qualified residence (a residence other than the principal "
        "residence). Points on a second home are deducted ratably over the "
        "life of the loan, because 26 U.S.C. 461(g)(2) allows a deduction in "
        "the year paid only for the principal residence. Exclude points "
        "already included in second_residence_mortgage_interest, and do not "
        "include them in home_mortgage_points."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/461#g",
        "https://www.irs.gov/pub/irs-pdf/p936.pdf#page=6",
    ]
