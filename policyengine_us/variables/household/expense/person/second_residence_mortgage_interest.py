from policyengine_us.model_api import *


class second_residence_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Interest paid on a second-residence mortgage"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
    documentation = (
        "Home mortgage interest on debt secured by the taxpayer's second "
        "qualified residence: a residence other than the principal residence, "
        "such as a vacation home, that the taxpayer treats as a qualified "
        "residence under 26 U.S.C. 163(h)(4)(A)(i)(II). Do not include it in "
        "home_mortgage_interest. Federal law pools it with principal-residence "
        "interest; some states allow only principal-residence interest."
    )
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_A",
        "https://www.irs.gov/pub/irs-pdf/p936.pdf#page=3",
    ]
