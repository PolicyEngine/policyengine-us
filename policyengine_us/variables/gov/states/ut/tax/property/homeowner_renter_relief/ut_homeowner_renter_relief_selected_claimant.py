from policyengine_us.model_api import *


class ut_homeowner_renter_relief_selected_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Selected claimant for Utah Homeowner's/Renter's Relief"
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=1"
    )
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pre_eligible = person.tax_unit(
            "ut_homeowner_renter_relief_pre_one_claimant_eligible", period
        )
        claimant = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        claimant_rank = person.get_rank(
            person.household,
            -age,
            condition=claimant & pre_eligible,
        )
        return tax_unit.any(claimant & pre_eligible & (claimant_rank == 0))
