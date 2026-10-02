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
        # PDF pages 7, 12, 17, 18.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=7",
        # PDF pages 9, 10.
        "https://liheapch.acf.gov/docs/2026/state-plans/NJ_Plan_2026.pdf#page=9",
    )
    documentation = "Annual regular heating payment, verified for FY2026. Earlier years use backfilled parameters and are unverified historical estimates. Amounts preserve all published grid anomalies; no expense cap applies. Unknown/unsupported direct fuels return zero. Separate fuel charges paid to landlords cannot be distinguished from vendor bills without a direct benefit override. Crisis, cooling, furnace and utility-program benefits are excluded."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.payment
        region = max_(spm_unit("nj_liheap_region", period), 1)
        size = p.household_size_group.calc(
            max_(spm_unit("nj_liheap_household_size", period), 1)
        )
        band = spm_unit("nj_liheap_income_band", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        deliverable = (
            (fuel == types.FUEL_OIL)
            | (fuel == types.KEROSENE)
            | (fuel == types.PROPANE)
            | (fuel == types.WOOD)
            | (fuel == types.COAL)
        )
        # FY2026 handbook 3.2.F assigns direct payers by their heating fuel.
        # The codified renter-level rule for subsidized direct payers differs.
        # Chapter 5:49 was readopted in 2025; the conflict remains unresolved.
        amount = select(
            [
                spm_unit("heat_expense_included_in_rent", period),
                fuel == types.ELECTRICITY,
                fuel == types.NATURAL_GAS,
                deliverable,
            ],
            [
                p.amount.renters[region][band][size],
                p.amount.electric[region][band][size],
                p.amount.gas[region][band][size],
                p.amount.deliverables[region][band][size],
            ],
            default=0,
        )
        # Unknown county is a payment-table coverage gap, not a legal denial.
        return where(spm_unit("nj_liheap_region", period) > 0, amount, 0)
