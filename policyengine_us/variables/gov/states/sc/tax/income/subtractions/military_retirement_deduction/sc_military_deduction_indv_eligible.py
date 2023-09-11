from policyengine_us.model_api import *


class sc_military_deduction_indv_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the South Carolina military deduction for eligible individuals"
    defined_for = StateCode.SC
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1171(A)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        return head | spouse
