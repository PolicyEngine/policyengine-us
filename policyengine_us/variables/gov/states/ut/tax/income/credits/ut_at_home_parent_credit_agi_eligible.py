from policyengine_us.model_api import *


class ut_at_home_parent_credit_agi_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Utah at-home parent credit based on adjusted gross income"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html",
        "https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent

        return tax_unit("adjusted_gross_income", period) <= p.max_agi
