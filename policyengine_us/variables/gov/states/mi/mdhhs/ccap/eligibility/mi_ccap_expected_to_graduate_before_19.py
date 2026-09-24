from policyengine_us.model_api import *


class mi_ccap_expected_to_graduate_before_19(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Expected to finish high school before age 19 for Michigan CDC"
    defined_for = StateCode.MI
    documentation = (
        "Whether the child is reasonably expected to complete high school before "
        "reaching age 19. Full-time high school enrollment is tested separately. "
        "Defaults to high-school enrollment and can be overridden per person."
    )
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=2"
    )

    def formula(person, period, parameters):
        # NOTE: default only. An enrolled high-school student is assumed to be
        # expected to finish before 19 unless this input is set explicitly,
        # mirroring sd_cca_expected_to_graduate.
        return person("is_in_secondary_school", period) | person(
            "is_in_k12_school", period
        )
