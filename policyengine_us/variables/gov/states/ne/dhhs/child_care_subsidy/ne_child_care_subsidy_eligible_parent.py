from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska Child Care Subsidy program eligible parent"
    definition_period = YEAR
    documentation = "Nebraska Child Care Subsidy eligible program parent must either be working, involved with Employment First as part of the ADC program, going to school or trainings, going to medical or therapy visits for self or child(ren), or ill or hurt (must be confirmed by a doctor)"
    reference = (
        "https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx",
    )
    defined_for = StateCode.NE
