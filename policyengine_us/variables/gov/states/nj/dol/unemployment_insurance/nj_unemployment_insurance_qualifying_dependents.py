from policyengine_us.model_api import *


class nj_unemployment_insurance_qualifying_dependents(Variable):
    value_type = int
    entity = Person
    label = (
        "New Jersey unemployment insurance qualifying dependents at claim establishment"
    )
    unit = "dependent"
    documentation = (
        "Count of dependents who satisfy N.J.S.A. 43:21-3(c)(2)(B), including "
        "an unemployed spouse or qualifying unmarried child. Phase-1 scope: "
        "callers should determine dependent status and the both-spouses-claim "
        "exclusion before inputting this count."
    )
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
        "https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml",
    )
    defined_for = StateCode.NJ
