from policyengine_us.model_api import *


class mi_ccap_requires_court_ordered_constant_care(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Requires constant care under a court order for Michigan CDC"
    defined_for = StateCode.MI
    documentation = (
        "Whether a court order establishes this child's need for constant care "
        "for the age-18 CDC eligibility pathway. General court supervision "
        "without this constant-care requirement is insufficient at age 18."
    )
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=2"
    )
