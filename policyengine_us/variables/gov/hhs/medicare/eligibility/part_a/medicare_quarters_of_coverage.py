from policyengine_us.model_api import *


class medicare_quarters_of_coverage(Variable):
    value_type = int
    entity = Person
    label = "Medicare quarters of coverage"
    documentation = (
        "Number of quarters of Social Security-covered employment. "
        "40 quarters required for premium-free Part A. Defaults to 40 "
        "because survey microdata does not observe work-history quarters "
        "and about 99% of beneficiaries qualify for premium-free Part A; "
        "without this default, microsimulation would charge every enrollee "
        "the full Part A premium. For noncitizens outside the citizen and "
        "five-year permanent resident routes, this input also decides Medicare "
        "eligibility, so it should reflect entitlement on the person's own or a "
        "spouse's record (42 U.S.C. 426(a)(2)(A) reaches monthly benefits under "
        "42 U.S.C. 402, including spouse benefits in 402(b) and (c)). The limit "
        "in 8 U.S.C. 1611(b)(3) to wages from authorized employment is not "
        "modeled."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/426#a",
        "https://www.law.cornell.edu/uscode/text/42/402",
        "https://www.law.cornell.edu/uscode/text/8/1611#b_3",
    )
    default_value = 40
    definition_period = YEAR
