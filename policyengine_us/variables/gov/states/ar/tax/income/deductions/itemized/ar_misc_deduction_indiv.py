from policyengine_us.model_api import *


class ar_misc_deduction_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas miscellaneous deduction when married filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR3_ItemizedDeduction.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.misc
        misc_ded = tax_unit("misc_deduction", period)
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        return max_(
            0,
            misc_ded - p.floor * agi,
        )
