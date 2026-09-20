from policyengine_us.model_api import *


class nj_ccap_has_cpp_referral(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.NJ
    label = "New Jersey CP&P child-care referral"
    documentation = "Whether CP&P has referred this child for subsidized child care under an approved protective-services case plan pursuant to N.J.A.C. 10:15-5.4. General court supervision alone does not establish a CP&P referral."
    reference = "https://www.nj.gov/humanservices/notices/documents/rules-and-regulations/NJAC%2010_15%20CHILD%20CARE%20SERVICES.PDF#page=52"
