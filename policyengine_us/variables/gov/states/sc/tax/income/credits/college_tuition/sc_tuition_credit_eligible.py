from policyengine_us.model_api import *


class sc_tuition_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the South Carolina Tuition Credit"
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",
        # South Carolina Legal Code | SECTION 12-6-3385 (B)(3)(b)
    )
