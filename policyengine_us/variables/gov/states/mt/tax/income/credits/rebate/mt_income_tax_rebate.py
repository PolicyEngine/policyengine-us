from policyengine_us.model_api import *


class mt_income_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana 2023 income tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html"
    defined_for = StateCode.MT

    # The rebate is based on 2021 income tax liability, but provided in 2023
    # we assume that the tax liability does not change between 2021 and 2023
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.rebate
        filing_status = tax_unit("filing_status", period)
        return p.amount[filing_status]
