from policyengine_us.model_api import *


class mt_income_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana 2021 income tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html"
    defined_for = StateCode.MT

    # The 2021 income tax rebate (MCA 15-30-2191, provided in 2023) is the
    # lesser of the 2021 income tax liability or a per-return cap ($1,250, or
    # $2,500 for a joint return). It is a one-time payment based on the return's
    # total liability rather than a credit claimed in a spouse's column, so it
    # is capped at the combined Montana income tax before refundable credits
    # (Form 2 line 20) and applied once per return. Modeling it as a per-column
    # non-refundable credit understated it when one spouse's separate liability
    # was below their share of the cap and distorted the separate-vs-joint
    # filing election (taxsim #1189).
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.rebate
        filing_status = tax_unit("filing_status", period)
        cap = p.amount[filing_status]
        liability = tax_unit("mt_income_tax_before_2021_rebate", period)
        return min_(cap, liability)
