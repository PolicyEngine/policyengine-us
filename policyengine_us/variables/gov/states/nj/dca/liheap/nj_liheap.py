from policyengine_us.model_api import *


class nj_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP regular heating benefit"
    unit = USD
    defined_for = "nj_liheap_eligible"
    reference = (
        "https://nj.gov/dca/dhcr/offices/docs/FY2026%20Benefit%20Matrix.pdf",
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20Benefit%20Matrix.png",
        # PDF pages 12, 18.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=12",
        # PDF pages 13, 19.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=13",
        # PDF pages 9, 10.
        "https://liheapch.acf.gov/docs/2026/state-plans/NJ_Plan_2026.pdf#page=9",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-2-2",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-3-2",
    )
    documentation = (
        "Annual regular heating payment, verified for FY2026 and FY2027. Earlier "
        "years back to FY2022 use backfilled parameters and are unverified estimates; "
        "before FY2022 the program is not modeled (eligibility/in_effect). Amounts "
        "preserve the published grid anomalies, including the FY2027 renters cell "
        "for Warren and Sussex households of 13 or more at $2,001 to $6,439 a month "
        "(474 against 471 in FY2026); no expense cap applies. A household with a "
        "rent subsidy or in "
        "public housing that pays its own heating bill receives the renters level "
        "under N.J.A.C. 5:49-2.2(d)1.i. Region 1 holds nineteen of the twenty-one "
        "counties. Other and unspecified direct fuels return zero as a coverage "
        "gap. Separate fuel charges paid to landlords cannot be distinguished from "
        "vendor bills without a direct benefit override. Crisis, cooling, furnace "
        "and utility-program benefits are excluded."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.payment
        region = max_(spm_unit("nj_liheap_region", period), 1)
        size = p.household_size_group.calc(
            max_(spm_unit("nj_liheap_household_size", period), 1)
        )
        # The floor keeps units outside New Jersey (band 0) on a valid grid key.
        band = max_(spm_unit("nj_liheap_income_band", period), 1)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        deliverable = (
            (fuel == types.FUEL_OIL)
            | (fuel == types.KEROSENE)
            | (fuel == types.PROPANE)
            | (fuel == types.WOOD)
            | (fuel == types.COAL)
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # N.J.A.C. 5:49-2.2(d)1.i pays a household with a rent subsidy that does
        # not cover all heating costs and a heating bill in its name at the
        # renter's level. The FY2026 handbook (2.2, page 6) copies (d)1 without
        # that subparagraph and prints no contrary rule, so the codified rule
        # applies. Public housing is read with the rent subsidy because 2.2(d)1
        # treats the two as one class; the rule names only the subsidy.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Handbook 3.2.F (page 12) assigns other direct payers by heating fuel. A
        # grid-tied solar home pays an electricity bill, the same pairing
        # heating_expense uses.
        amount = select(
            [
                heat_in_rent | subsidized,
                (fuel == types.ELECTRICITY) | (fuel == types.SOLAR),
                fuel == types.NATURAL_GAS,
                deliverable,
            ],
            [
                p.amount.renters[region][band][size],
                p.amount.electric[region][band][size],
                p.amount.gas[region][band][size],
                p.amount.deliverables[region][band][size],
            ],
            # Other and unspecified fuels have no panel; the unspecified default
            # is tracked in #9754.
            default=0,
        )
        # Unknown county is a payment-table coverage gap, not a legal denial.
        return where(spm_unit("nj_liheap_region", period) > 0, amount, 0)
