from policyengine_us.model_api import *


class md_meap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP countable household income"
    unit = USD
    defined_for = StateCode.MD
    reference = ("https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",)
    documentation = (
        "Annual income approximates the 30-day application period. All members' income "
        "counts in full. Follows COMAR exclusions for nonrecurring lump sums and "
        "AmeriCorps/VISTA despite conflicting manual/plan checklists. Reported child "
        "support paid is assumed court-ordered. Veterans income approximates pension "
        "benefits and strike income is assumed not employee-funded. TDAP, royalties, "
        "gifts, loans, special allowances and home-care receipts cannot be isolated "
        "reliably. Medicare-premium deductions remain deferred. Rental income is "
        "assumed nonnegative."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.income
        # COMAR 07.03.21.04D(3), D(26) and E(20) count Social Security and
        # railroad retirement benefits less the Medicare payment deduction.
        # medicare_part_b_premium and medicare_part_b_premiums_reported are not
        # wired in yet, so both benefits count gross.
        # The TANF source applies take-up to Maryland TCA entitlement.
        income = add(spm_unit, period, ["md_meap_countable_earned_income"]) + add(
            spm_unit, period, p.sources.unearned
        )
        return max_(income - add(spm_unit, period, ["child_support_expense"]), 0)
