from policyengine_us.model_api import *


class ar_misc_deduction_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas miscellaneous deduction when married filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ark. Code § 26-51-437(a), enacted by Act 382 of 1987, § 28
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F1987R%2FPublic%2F&file=382.pdf&ddBienniumSession=1987%2F1987R#page=9",
        # 2025 Form AR3 instructions, Lines 20-25
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=21",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=22",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        # Arkansas did not adopt the federal suspension of miscellaneous
        # itemized deductions, so start from the expenses, not misc_deduction.
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.misc
        expenses = tax_unit("total_misc_deductions", period)
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        return max_(0, expenses - p.income_floor * agi)
