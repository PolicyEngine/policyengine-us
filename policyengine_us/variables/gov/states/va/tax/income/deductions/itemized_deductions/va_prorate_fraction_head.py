from policyengine_us.model_api import *


class va_prorate_fraction_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia joint amount proration fraction of head"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "§ 58.1-322.03.(1.a.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18",
    )
    defined_for = StateCode.VA

    # get proportion of head's share in the combined federal adjusted gross income.
    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        federal_agi_head = person("adjusted_gross_income_head", period)
        federal_agi = tax_unit("adjusted_gross_income", period)
        prorate_fraction_head = federal_agi_head / federal_agi
        return prorate_fraction_head[0]
