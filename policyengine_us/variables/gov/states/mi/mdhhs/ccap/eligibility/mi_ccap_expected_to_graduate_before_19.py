from policyengine_us.model_api import *


class mi_ccap_expected_to_graduate_before_19(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Expected to finish high school before age 19 for Michigan CDC"
    defined_for = StateCode.MI
    documentation = (
        "Whether the child is reasonably expected to complete high school before "
        "reaching age 19. Full-time high school enrollment is tested separately."
    )
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=2"
    )
