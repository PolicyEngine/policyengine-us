from policyengine_us.model_api import *


class il_ihwap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Illinois IHWAP categorically eligible"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/6862#7",
        "https://dceo.illinois.gov/communityservices/homeweatherization.html",
    )
    adds = "gov.states.il.dceo.ihwap.eligibility.categorical_eligibility"
