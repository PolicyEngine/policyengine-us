from policyengine_us.model_api import *


class sc_military_deduction_indv(Variable):
    value_type = float
    entity = Person
    label = "South Carolina military deduction for eligible individuals"
    defined_for = "sc_military_deduction_indv_eligible"
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1171(A)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    adds = ["military_retirement_pay"]
