from policyengine_us.model_api import *


class al_gambling_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama gambling loss deduction"
    unit = USD
    documentation = (
        "Alabama itemized deduction for gambling losses, to the extent of "
        "gambling winnings and not subject to the 2% limit on miscellaneous "
        "deductions. Alabama does not follow the federal 90% limit that "
        "starts in 2026."
    )
    definition_period = YEAR
    reference = (
        # 2025 Form 40 booklet, Schedule A line 25
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=21",
        # Ala. Admin. Code r. 810-3-17-.01
        "https://admincode.legislature.state.al.us/api/rule/810-3-17-.01",
        # ALDOR summary of P.L. 119-21: section 165(d), "Tied to Federal: No"
        # PDF pages 9-10
        "https://www.revenue.alabama.gov/wp-content/uploads/2025/11/OBBBA-Executive-Summary_FinalwAppendixA_10.31.25.pdf#page=9",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        # Dependents report their gambling on their own returns.
        losses = tax_unit_non_dep_add(tax_unit, period, ["gambling_losses"])
        winnings = tax_unit_non_dep_add(tax_unit, period, ["gambling_winnings"])
        return min_(losses, winnings)
