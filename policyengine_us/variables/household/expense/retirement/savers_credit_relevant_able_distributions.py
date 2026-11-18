from policyengine_us.model_api import *


class savers_credit_relevant_able_distributions(Variable):
    value_type = float
    entity = Person
    label = "ABLE distributions that reduce saver's credit contributions"
    documentation = (
        "Distributions from the person's ABLE account that reduce their "
        "qualified contributions for the saver's credit under 26 U.S.C. "
        "25B(d)(2): those received in the statutory testing period, after "
        "the statute's exceptions and including any amount the spouse rule "
        "attributes to the person. Distributions from retirement plans and "
        "IRAs do not belong here."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25B#d_2",
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/pdf/PLAW-119publ21.pdf#page=97",
    )
