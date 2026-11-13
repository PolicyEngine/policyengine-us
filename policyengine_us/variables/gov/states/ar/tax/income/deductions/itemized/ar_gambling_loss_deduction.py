from policyengine_us.model_api import *


class ar_gambling_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas gambling loss deduction"
    unit = USD
    documentation = (
        "Gambling losses, deductible to the extent of gambling winnings and "
        "not subject to the 2% limitation on miscellaneous itemized deductions."
    )
    definition_period = YEAR
    reference = (
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2F&file=155.pdf&ddBienniumSession=2017%2F2017R#page=9",
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2017R%2FPublic%2F&file=155.pdf&ddBienniumSession=2017%2F2017R#page=10",
        "https://www.dfa.arkansas.gov/wp-content/uploads/208-GamblingIncomeExpenses.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=22",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        # Ark. Code § 26-51-424(a)(2)(B), as amended by Act 155 of 2017, § 21,
        # for tax years beginning on or after January 1, 2015 (§ 25): gambling
        # losses are deductible to the extent of gambling winnings and are not
        # subject to the 2% floor on miscellaneous itemized deductions, so the
        # deduction sits outside ar_misc_deduction_{joint,indiv}. DFA Subject
        # 208 has stated the same rule since at least 2009.
        losses = add(tax_unit, period, ["gambling_losses"])
        winnings = add(tax_unit, period, ["gambling_winnings"])
        return min_(losses, winnings)
