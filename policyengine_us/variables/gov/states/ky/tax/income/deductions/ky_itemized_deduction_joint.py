from policyengine_us.model_api import *


class ky_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf"
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    )
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        # If filing a joint return, only one standard deduction is allowed
        is_head = person("is_tax_unit_head", period)
        itemized_deductions = person.tax_unit(
            "ky_itemized_deductions_unit", period
        )

        return is_head * itemized_deductions
