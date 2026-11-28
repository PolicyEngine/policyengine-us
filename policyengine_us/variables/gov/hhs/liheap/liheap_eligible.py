from policyengine_us.model_api import *


class liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for regular LIHEAP heating or cooling assistance"
    documentation = (
        "Whether the household is eligible for its state's regular LIHEAP "
        "heating or cooling benefit. heating_type is a required input: most "
        "states' heating eligibility is false while it is unset. An eligible "
        "household can have a liheap payment of zero, for example when the "
        "state's benefit table has no amount for its fuel, or under "
        "Delaware's cooling benefit, which has no fixed amount. Leaves out "
        "Michigan's Home Heating Credit, and crisis, weatherization and "
        "equipment assistance."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/8624#b_2"
    adds = "gov.hhs.liheap.regular_eligibility"
