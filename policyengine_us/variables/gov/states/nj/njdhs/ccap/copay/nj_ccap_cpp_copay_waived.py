from policyengine_us.model_api import *


class nj_ccap_cpp_copay_waived(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.NJ
    label = "New Jersey CP&P approved child-care copay waiver"
    documentation = "Whether CP&P has approved a full copay waiver for this child's protective child care under N.J.A.C. 10:15-9.1(f). A referral alone does not waive the copay for care in the child's own home. A partially reduced assessed family copay can be supplied as nj_ccap_copay."
    reference = "https://www.nj.gov/humanservices/notices/documents/rules-and-regulations/NJAC%2010_15%20CHILD%20CARE%20SERVICES.PDF#page=85"
