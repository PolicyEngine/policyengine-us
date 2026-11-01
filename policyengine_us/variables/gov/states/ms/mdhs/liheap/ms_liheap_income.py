from policyengine_us.model_api import *


class ms_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP countable annual household income"
    defined_for = StateCode.MS
    reference = (
        # Rule 6.3 B-C (page 23) and Rule 6.11 A-K (pages 29-33).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=29",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        person = spm_unit.members
        adult = person("age", period) >= p.adult_age
        # Rule 6.11 I(1) specifies Schedule C's Net Profit or (Loss) line / 12.
        # Rule 6.11 C(2) counts self-employment income and I(2) uses a farmer as
        # its example, so farm operations income is counted the same signed way.
        # Rule 6.11 I(1) does not say whether a loss is floored at zero. The
        # signed amount is counted, so a business or farm loss offsets wages
        # and other members' income, and the household total is floored at zero.
        # Do not deduct business expenses again. Annual inputs approximate the
        # annualized preceding 30 days; pay-frequency changes and court-emancipated
        # minors are not identified by existing inputs.
        self_employment = add(
            person,
            period,
            [
                "self_employment_income",
                "sstb_self_employment_income",
                "farm_operations_income",
            ],
        )
        wages = max_(person("employment_income", period), 0)
        earned = (wages + self_employment) * adult
        # Rule 6.3 B-C leave undocumented members out of household size and
        # count their income. Rule 6.11 J(2) says a minor's Social Security or
        # SSI "must be included and is listed under the parent or legal
        # guardian in the household", so a minor's unearned income is counted
        # as the adult's line in every household, including one whose head is
        # undocumented. Rule 6.11 D(3) and J(1) exclude a minor's earnings.
        # Medicare withholding is included in SSA. Child support, TANF, refunds,
        # foster care, and occasional receipts are excluded. Existing input totals
        # cannot isolate recurring versus occasional gifts/rent/interest, or all
        # countable insurance proceeds, royalties, jury duty, and recurring prizes.
        unearned = max_(add(person, period, p.unearned_income_sources), 0)
        return max_(spm_unit.sum(earned + unearned), 0)
