from policyengine_us.model_api import *


class sc_military_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina military retirement deduction"
    defined_for = StateCode.SC
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1171(A)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    adds = [
        "sc_military_deduction_indv",  # p4, p5
        "sc_military_deduction_survivors",  # p6
    ]
