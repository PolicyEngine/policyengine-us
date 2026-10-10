from policyengine_us.model_api import *


class hi_tax_credit_for_low_income_household_renters(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii low income household renters tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "hi_tax_credit_for_low_income_household_renters_eligible"
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=48",
        "https://files.hawaii.gov/tax/forms/2025/schx_i.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc

        # Schedule X lines 8-10 count only people who cannot be claimed as a
        # dependent by another taxpayer, with an extra exemption for each
        # such filer aged 65 or over. A return on which a filer can be
        # claimed generally claims no dependents (IRS Publication 501,
        # Dependent Taxpayer Test). Its filing exception restores the
        # return's own dependents, while claimable filers and their age
        # additions remain excluded.
        aged_head = (tax_unit("age_head", period) >= p.aged_age_threshold) & ~tax_unit(
            "head_is_dependent_elsewhere", period
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.aged_age_threshold
        ) & ~tax_unit("spouse_is_dependent_elsewhere", period)
        aged_exemptions = aged_head.astype(int) + aged_spouse.astype(int)

        dependent_taxpayer = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        filers = add(tax_unit, period, ["is_tax_unit_head_or_spouse"])
        dependent_filers = filers - independent_filers
        ordinary_exemptions = max_(
            tax_unit("exemptions_count", period) - dependent_filers, 0
        )
        exemptions = where(dependent_taxpayer, independent_filers, ordinary_exemptions)

        total_exemptions = exemptions + aged_exemptions
        return p.amount * total_exemptions
