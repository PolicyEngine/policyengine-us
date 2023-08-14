from policyengine_us.model_api import *


class va_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "VA itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacode/58.1-322.03/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        deductions = person.tax_unit("va_itemized_deductions_unit", period)
        is_head = person("is_tax_unit_head", period)
        return deductions * is_head
