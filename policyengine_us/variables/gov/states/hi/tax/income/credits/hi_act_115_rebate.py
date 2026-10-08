from policyengine_us.model_api import *


class hi_act_115_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii ACT 115 rebate"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.hawaii.gov/act-115-ref/",
        "https://data.capitol.hawaii.gov/sessions/session2022/bills/SB514_CD2_.HTM",
        "https://files.hawaii.gov/tax/news/announce/ann22-03.pdf#page=2",
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=45",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.act_115_rebate
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        federal_agi = tax_unit("adjusted_gross_income", period)
        amount_per_exemption = select(
            [
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
            ],
            [
                p.joint.calc(federal_agi),
                p.single.calc(federal_agi),
                p.single.calc(federal_agi),
                p.joint.calc(federal_agi),
            ],
            default=p.single.calc(federal_agi),
        )
        # The refund is multiplied by the number of qualified exemptions.
        # Additional exemptions for age or disability do not count, so each
        # person in the tax unit is one exemption.
        exemptions = tax_unit("exemptions_count", period)
        # A person who can be claimed as a dependent by another taxpayer is
        # not a qualifying resident taxpayer, and each qualifying resident
        # taxpayer claims the refund for the exemptions they are entitled to.
        # A filer who can be claimed has no exemption (HRS 235-54(a)), and a
        # return on which a filer can be claimed claims no dependents (IRS
        # Publication 501), so such a return counts only the filers who
        # cannot be claimed.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        qualified_exemptions = where(dependent_filer, independent_filers, exemptions)
        return amount_per_exemption * qualified_exemptions
