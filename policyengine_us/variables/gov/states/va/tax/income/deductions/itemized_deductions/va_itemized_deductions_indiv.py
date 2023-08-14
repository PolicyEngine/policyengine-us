from policyengine_us.model_api import *


class va_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Virginia itemized deduction for individual couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacode/58.1-322.03/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        unit_deds = person.tax_unit("va_itemized_deductions_unit", period)
        return unit_deds * person("indiv_share_agi", period)
