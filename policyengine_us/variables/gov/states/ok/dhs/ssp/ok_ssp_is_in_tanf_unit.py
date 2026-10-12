from policyengine_us.model_api import *


class ok_ssp_is_in_tanf_unit(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma TANF benefit includes this person"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    documentation = "Verified inclusion of the person's needs in the TANF grant, rather than merely being the payee. Explicit input avoids a TANF/SSP eligibility cycle."
