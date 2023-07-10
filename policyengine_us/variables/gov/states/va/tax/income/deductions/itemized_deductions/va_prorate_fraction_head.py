from policyengine_us.model_api import *


class va_prorate_fraction(Variable):
    value_type = float
    entity = Person
    label = "Virginia joint amount proration fraction of head"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/","§ 58.1-322.03.(1.a.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18"
    )
    defined_for = StateCode.VA

    # get proportion of head's share in the combined federal adjusted gross income.
    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        federal_agi = tax_unit("adjusted_gross_income", period)
        head = person("is_tax_unit_head", period)
        head_agi = federal_agi * head
        
        return head_agi / federal_agi
