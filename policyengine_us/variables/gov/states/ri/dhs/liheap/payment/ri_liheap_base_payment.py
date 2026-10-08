from policyengine_us.model_api import *


class ri_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP primary heating payment with utility enhancement"
    documentation = (
        "Ordinary primary heating payment, including the federal matrix grant "
        "and the state enhancement for a qualifying primary gas or electric "
        "utility account. This component assumes the modeled primary grant "
        "reaches the qualifying utility account; it does not determine final "
        "eligibility or select a heat-in-rent payment route."
    )
    defined_for = StateCode.RI
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://dhs.ri.gov/media/9696/download?language=en",
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        # PUC 1-5: the utility credits the enhancement only after receiving
        # the household's federal grant.
        "https://ripuc.ri.gov/sites/g/files/xkgbur841/files/2025-11/LIHEAP%2025-38-GE_PUC%20Data%20Requests%20Set%201%20to%20DHS%20update.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap.payment
        band = max_(spm_unit("ri_liheap_income_band", period), 1)
        subsidized = spm_unit.household("is_in_public_housing", period) | spm_unit(
            "receives_housing_assistance", period
        )
        # Same primary heating obligation test as ri_liheap_eligible.
        primary_bill = spm_unit("has_heating_expense", period) | (
            spm_unit("heating_expense", period) > 0
        )
        # Matrix row F uses the lowest payment for subsidized households
        # responsible for their primary heating bill, regardless of income band.
        band = where(subsidized & primary_bill, len(p.fpg_rates) + 1, band)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        deliverable = (
            (fuel == fuels.FUEL_OIL)
            | (fuel == fuels.KEROSENE)
            | (fuel == fuels.PROPANE)
            | (fuel == fuels.WOOD)
        )
        amount = select(
            [deliverable, fuel == fuels.NATURAL_GAS, fuel == fuels.ELECTRICITY],
            [
                p.amount.deliverables[band],
                p.amount.natural_gas[band],
                p.amount.electricity[band],
            ],
            # NONE means no heating. No supported schedule mapping was found
            # for COAL, OTHER, SOLAR or UNSPECIFIED; their zero is an unverified
            # estimate, not a legal denial of assistance.
            default=0,
        )
        utility_fuel = (fuel == fuels.NATURAL_GAS) | (fuel == fuels.ELECTRICITY)
        # Existing inputs do not identify the utility provider or the account
        # receiving the federal grant. For this ordinary primary component,
        # assume a qualifying distribution-company account and grant receipt.
        # Block Island Utility District and Clear River Electric and Water
        # District (formerly Pascoag) are excluded by law, but state/county
        # alone cannot identify every account. No enhancement goes to
        # deliverable fuels, unpriced fuels, or a direct $400 HIR payment.
        enhancement = where(utility_fuel & (amount > 0), p.utility_enhancement, 0)
        # This ungated primary payment has no actual-expense cap. It does not
        # calculate the unresolved HIR routes or establish final eligibility.
        size = spm_unit("ri_liheap_household_size", period)
        # Payment amounts are sourced from FY2026 onward. Before October 1,
        # 2025, in_effect is false and the modeled payment is zero rather
        # than the different, unlocated FY2025 schedule.
        return where((size > 0) & p.in_effect, amount + enhancement, 0)
