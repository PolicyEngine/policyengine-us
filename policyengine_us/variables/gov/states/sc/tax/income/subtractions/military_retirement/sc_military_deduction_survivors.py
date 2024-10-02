from policyengine_us.model_api import *


class sc_military_deduction_survivors(Variable):
    value_type = float
    entity = Person
    label = "South Carolina military retirement deduction for survivors"
    defined_for = StateCode.SC
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1171(C)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("military_retirement_pay_survivors", period)
