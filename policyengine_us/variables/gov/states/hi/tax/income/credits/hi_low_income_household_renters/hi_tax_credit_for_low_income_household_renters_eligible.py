from policyengine_us.model_api import *


class hi_tax_credit_for_low_income_household_renters_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Hawaii low income household renters tax credit"
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=105",  # §18-235-55.7 (b)
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=48",
        "https://files.hawaii.gov/tax/forms/2025/schx_i.pdf#page=1",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # HRS 235-55.7(b) allows the credit to each resident taxpayer who
        # cannot be claimed as a dependent. Schedule X stops at line 3 only
        # for the first-listed filer; since a couple may list either spouse
        # first, a joint return qualifies unless both spouses can be claimed.
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        p = parameters(period).gov.states.hi.tax.income.credits.lihrtc
        agi = tax_unit("hi_agi", period)
        rent = add(tax_unit, period, ["rent"])
        return (
            (rent > p.eligibility.rent_threshold)
            & (agi < p.eligibility.agi_limit)
            & ~every_filer_dependent
        )
