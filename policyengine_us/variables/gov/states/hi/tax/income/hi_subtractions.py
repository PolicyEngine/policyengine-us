from policyengine_us.model_api import *


class hi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii subtractions from federal adjusted gross income"
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13",
        # Line 13: qualifying pension distributions "were included in your
        # federal AGI and will be excluded on this line."
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=13",
        # Filing requirements: dependents file with their own threshold.
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=4",
    )
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.subtractions
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so only the head's and spouse's amounts are subtracted.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
