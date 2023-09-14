from policyengine_us.model_api import *


class co_federal_ctc_child_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (child) replicated to account for the Colorado state CTC child eligibility"
    unit = USD
    documentation = "The CTC entitlement in respect of this person as a child."
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

    def formula(person, period, parameters):
        age = person("age", period)
        base_amount = parameters(period).gov.irs.credits.ctc.amount.base
        is_dependent = person("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        eligible = is_dependent & (age < p.age_threshold)
        return base_amount.calc(age) * eligible
