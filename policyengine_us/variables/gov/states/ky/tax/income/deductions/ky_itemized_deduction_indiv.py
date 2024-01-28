from policyengine_us.model_api import *


class ky_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky itemized deductions when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf"
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"  # (2)(i)
    )
    defined_for = "ky_can_file_separate_on_same_return"

    def formula(person, period, parameters):

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        itemized_deductions = person.tax_unit("ky_itemized_deductions_unit", period)

        return head_or_spouse * itemized_deductions
