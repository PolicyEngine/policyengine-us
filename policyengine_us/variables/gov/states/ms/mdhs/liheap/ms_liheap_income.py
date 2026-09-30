from policyengine_us.model_api import *


class ms_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP countable annual household income"
    defined_for = StateCode.MS
    reference = "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=22,23,24,29,30,31,32,33"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        person = spm_unit.members
        adult = person("age", period) >= p.adult_age
        # Rule 6.11 I(1) specifies Schedule C's Net Profit or (Loss) line / 12.
        # Preserve the signed net amount: a loss can offset other household income.
        # Do not deduct business expenses again. Annual inputs approximate the
        # annualized preceding 30 days; pay-frequency changes and court-emancipated
        # minors are not identified by existing inputs.
        earned = (
            max_(person("employment_income", period), 0)
            + person("self_employment_income", period)
        ) * adult
        # Rule 6.3(B)-(C) retains non-applicants' countable income without
        # headcount proration; Rule 6.11 still controls source/age exclusions.
        # Children's unearned benefits count in full.
        # Medicare withholding is included in SSA. Child support, TANF, refunds,
        # foster care, and occasional receipts are excluded. Existing input totals
        # cannot isolate recurring versus occasional gifts/rent/interest, or all
        # countable insurance proceeds, royalties, jury duty, and recurring prizes.
        unearned = max_(add(person, period, p.unearned_income_sources), 0)
        return max_(spm_unit.sum(earned + unearned), 0)
