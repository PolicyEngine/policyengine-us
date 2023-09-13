from policyengine_us.model_api import *


class sc_military_deduction_indv(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina military deduction for eligible individuals"
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1171(A)
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        military_retirement_pay = (
            person("military_retirement_pay", period) * head_or_spouse
        )
        return tax_unit.sum(military_retirement_pay)
