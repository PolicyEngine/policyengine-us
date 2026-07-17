from policyengine_us.model_api import *


class mt_income_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana 2021 income tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html"
    defined_for = StateCode.MT

    # The rebate is based on 2021 income tax liability, but provided in 2023.
    # MCA 15-30-2191(2)(b): the rebate is the LESSER of the filing-status
    # amount or the taxpayer's income tax liability, so it can not drive the
    # liability negative. Montana elects the lower of the joint and
    # separate-column computations, but that election
    # (mt_files_separately) depends on post-credit liability and would
    # create a computation cycle here, so cap at the smaller of the two
    # pre-credit bases — never larger than the elected one.
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.rebate
        filing_status = tax_unit("filing_status", period)
        liability_indiv = add(
            tax_unit,
            period,
            ["mt_income_tax_before_non_refundable_credits_indiv"],
        )
        liability_joint = tax_unit(
            "mt_income_tax_before_non_refundable_credits_joint", period
        )
        liability = min_(liability_indiv, liability_joint)
        return min_(p.amount[filing_status], max_(liability, 0))
