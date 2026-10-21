from policyengine_us.model_api import *


class ca_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California miscellaneous itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17076",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca.pdf#page=6",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.misc
        expenses = tax_unit("total_misc_deductions", period)
        # Schedule CA Part II lines 23-25 use federal AGI and floor the
        # percentage amount at zero. R&TC 17076(c) excludes IRC 67(g).
        floor = p.floor * tax_unit("positive_agi", period)
        return max_(expenses - floor, 0)
