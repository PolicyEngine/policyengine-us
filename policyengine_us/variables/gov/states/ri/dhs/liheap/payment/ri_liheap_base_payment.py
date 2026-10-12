from policyengine_us.model_api import *


class ri_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Rhode Island LIHEAP primary heating payment with utility enhancement"
    documentation = (
        "Ordinary primary heating payment, including the federal matrix grant "
        "and the state enhancement when the grant reaches a qualifying gas "
        "or electric utility account. For heat in rent, a reported separate "
        "electric bill selects the secondary-electric route; otherwise the "
        "grant is paid directly. Utility-provider and account ownership "
        "requirements are assumed satisfied. Final eligibility is separate."
    )
    defined_for = StateCode.RI
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/RI_BenefitMatrix_2026.pdf",
        "https://dhs.ri.gov/media/9696/download?language=en",
        # PDF pages 5-6: heat-in-rent payment and subsidized utility burden.
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=5",
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
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        separate_electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        hir = p.heat_in_rent
        secondary_electric_payment = where(
            subsidized, hir.subsidized_secondary_electric, hir.secondary_electric
        )
        # Rows H-I apply to the secondary electric account. Row G is the
        # direct grant when there is no separate electric bill to credit.
        # Subsidized tenants without a utility burden are ineligible.
        heat_in_rent_payment = where(
            separate_electric_bill,
            secondary_electric_payment,
            where(subsidized, 0, hir.direct),
        )
        amount = where(heat_in_rent, heat_in_rent_payment, amount)
        utility_fuel = (fuel == fuels.NATURAL_GAS) | (fuel == fuels.ELECTRICITY)
        utility_grant = where(heat_in_rent, separate_electric_bill, utility_fuel)
        # Existing inputs do not identify the utility provider or the account
        # receiving the federal grant. For this ordinary primary component,
        # assume a qualifying distribution-company account and grant receipt,
        # including the first regular grant to a secondary electric account.
        # Block Island Utility District and Clear River Electric and Water
        # District (formerly Pascoag) are excluded by law, but state/county
        # alone cannot identify every account. No enhancement goes to
        # deliverable fuels, unpriced fuels, or a direct $400 HIR payment.
        enhancement = where(utility_grant & (amount > 0), p.utility_enhancement, 0)
        # The regular grant has no actual-expense cap. Earlier backfilled
        # results are unverified estimates, not a policy start date.
        size = spm_unit("ri_liheap_household_size", period)
        return where((size > 0) & (fuel != fuels.NONE), amount + enhancement, 0)
