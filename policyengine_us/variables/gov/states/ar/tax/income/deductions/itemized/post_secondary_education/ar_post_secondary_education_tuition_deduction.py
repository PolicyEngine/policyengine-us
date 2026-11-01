from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/wp-content/uploads/AR1075_2022.pdf#page=1"
    defined_for = StateCode.AR

    adds = ["ar_post_secondary_education_tuition_deduction_person"]
