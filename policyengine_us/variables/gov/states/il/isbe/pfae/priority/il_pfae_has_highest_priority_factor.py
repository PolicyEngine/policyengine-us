from policyengine_us.model_api import *


class il_pfae_has_highest_priority_factor(Variable):
    value_type = bool
    entity = Person
    label = "Has highest priority selection factor for Illinois PFAE"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Highest priority selection factors (50 points each):
        # 1. Homeless (McKinney-Vento)
        # 2. Child welfare involvement (foster care, Ward of State)
        # 3. Has IEP or referred for special education evaluation
        # 4. Family income at or below 50% FPL and/or receiving TANF
        # Factor 1: Homeless
        is_homeless = person.household("is_homeless", period)

        # Factor 2: Child welfare involvement (foster care)
        is_in_foster_care = person("is_in_foster_care", period)

        # Factor 3: Has IEP
        has_iep = person("has_individualized_education_program", period)

        # Factor 4: Income <= 50% FPL OR receiving TANF
        is_deep_poverty = person("il_pfae_is_deep_poverty", period)
        receives_tanf = person.spm_unit("il_tanf", period) > 0

        return (
            is_homeless
            | is_in_foster_care
            | has_iep
            | is_deep_poverty
            | receives_tanf
        )
