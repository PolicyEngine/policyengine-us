from policyengine_us.model_api import *


class ca_tanf_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Exempt Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/ord/entres/getinfo/pdf/12EAS.pdf#page=45"

    # Known simplification: exempt status regulation may require ALL adult
    # caretakers in the AU to qualify, not just any member. The current
    # adds pattern treats any qualifying member as sufficient.
    adds = "gov.states.ca.cdss.tanf.cash.exempt"
