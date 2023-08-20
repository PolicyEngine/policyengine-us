from policyengine_us.model_api import *


class co_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado child tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129. Child tax credit - legislative declaration - definitions.
        "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal",
        # 2022 Colorado Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1",
        # Colorado Individual Income Tax Filing Guide - Instructions for Select Credits from the DR 0104CR - Line 1 Child Tax Credit
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        person = tax_unit.members
        # The co ctc amount is based on agi, federal ctc amount and number of eligible children.
        agi = tax_unit("adjusted_gross_income", period)
        federal_ctc = tax_unit("ctc", period)
        child_age_eligible = person("age", period) < p.age_threshold
        eligible_child = (
            person("ctc_qualifying_child", period) & child_age_eligible
        )
        eligible_children = tax_unit.sum(eligible_child)

        rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rate.single.calc(agi, right=True),
                p.rate.joint.calc(agi, right=True),
                p.rate.separate.calc(agi, right=True),
                p.rate.widow.calc(agi, right=True),
                p.rate.head_of_household.calc(agi, right=True),
            ],
        )
        return rate * federal_ctc * eligible_children
