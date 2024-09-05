from policyengine_us.model_api import *


class sc_tuition_credit(Variable):
    value_type = float
    entity = Person
    label = "South Carolina Tuition Credit"
    defined_for = "sc_tuition_credit_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php",
        # South Carolina Legal Code | SECTION 12-6-3385 (A)
    )
