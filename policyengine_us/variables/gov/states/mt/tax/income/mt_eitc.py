from policyengine_us.model_api import *


class mt_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0180/0150-0300-0230-0180.html"

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        filing_status = tax_unit("filing_status", period)
        rate = parameters(period).gov.states.mt.tax.income.credits.eitc.rate
        return where(
            filing_status == filing_status.possible_values.SEPARATE,
            0,
            eitc * rate,
        )
