from policyengine_us.model_api import *


class md_meap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP countable household income"
    unit = USD
    defined_for = StateCode.MD
    reference = ("https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",)
    documentation = "Annual income approximates the 30-day application period. All members' income counts in full. Follows COMAR exclusions for nonrecurring lump sums and AmeriCorps/VISTA despite conflicting manual/plan checklists. Reported child support paid is assumed court-ordered. Veterans income approximates pension benefits and strike income is assumed not employee-funded. TDAP, royalties, gifts, loans, special allowances, home-care receipts and Medicare premiums beyond Part B are unsupported. Rental income is assumed nonnegative."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.income
        person = spm_unit.members
        retirement = add(person, period, ["social_security", "railroad_benefits"])
        net_retirement = spm_unit.sum(
            max_(retirement - person("medicare_part_b_premium", period), 0)
        )
        income = (
            add(spm_unit, period, ["md_meap_countable_earned_income"])
            + add(spm_unit, period, p.sources.unearned)
            + net_retirement
        )
        return max_(income - add(spm_unit, period, ["child_support_expense"]), 0)
