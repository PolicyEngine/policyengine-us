from policyengine_us.model_api import *


class ok_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Oklahoma LIHEAP regular heating assistance"
    defined_for = StateCode.OK
    # OAC 340:20-1-10(c)-(h), 340:20-1-11(a), 340:20-1-19(d): eligible size,
    # gross income including deemed contributions, and heating responsibility.
    reference = (
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://liheapch.acf.gov/docs/2026/state-plans/OK_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ok_liheap_household_size", period)
        # OAC 340:20-1-11(a) converts income to a monthly amount and rounds it
        # to the nearest dollar; Appendix C-7 prints whole-dollar monthly
        # limits. Rounding the monthly total half up approximates the
        # per-source rounding.
        income = spm_unit("ok_liheap_gross_income", period)
        monthly_income = np.floor(income / MONTHS_IN_YEAR + 0.5)
        monthly_limit = spm_unit("ok_liheap_income_limit", period) / MONTHS_IN_YEAR
        fuel = spm_unit("heating_type", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # OAC 340:20-1-19(d)(1) pays "renters, roomers, and boarders who pay a
        # surcharge for utilities included in their rent", and (d)(2) verifies
        # "the surcharge" by a landlord statement, a lease, or "a rent receipt
        # designating that the fuel cost is separate from the total shelter
        # payment". 340:20-1-10(h) denies households that do not verify
        # responsibility for energy costs. The FY2026 plan, item 2.3 (page 9),
        # agrees: heat-in-rent renters "must verify that a specific portion of
        # the rent is for utilities or be charged a surcharge". A positive
        # primary fuel bill represents that charge for every heat-in-rent
        # renter or roomer, subsidized or not; the flag alone does not.
        # NOTE: 340:20-1-10(c) counts "undesignated payments for energy in the
        # form of rent", and 340:20-1-10(f)(3) names only "subsidized
        # households whose heating or cooling costs are included in the rent"
        # as non-vulnerable. Reading those to pay an unsubsidized renter with
        # no surcharge is not followed: (c) defines the household unit and
        # (f) lists examples.
        has_bill = spm_unit("heating_expense", period) > 0
        # A direct obligation may be reported with the flag; it represents the
        # household's remaining cost after any utility allowance.
        pays_directly = ~heat_in_rent & spm_unit("has_heating_expense", period)
        # Roomer relatedness, shared-meter/institutional facts, and tribal
        # LIHEAP receipt are not available as existing inputs.
        return (
            (size > 0)
            & (monthly_income <= monthly_limit)
            & (fuel != fuel.possible_values.NONE)
            & (has_bill | pays_directly)
        )
