from policyengine_us.model_api import *


class home_mortgage_points(Variable):
    value_type = float
    entity = Person
    label = "Deductible points paid on a home mortgage"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "Points on debt secured by a qualified home that are deductible this "
        "year: points deductible in the year paid under 26 U.S.C. 461(g)(2), "
        "plus this year's ratable share of points deducted over the life of "
        "a loan. Exclude points already included in home_mortgage_interest. "
        "Points reported on Form 1098 usually are, because Schedule A line 8a "
        "combines them with interest, so this is typically Schedule A line 8c, "
        "points not reported on Form 1098."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/461#g_2",
        "https://www.irs.gov/pub/irs-pdf/p936.pdf#page=6",
    ]
