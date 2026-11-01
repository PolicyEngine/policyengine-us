from policyengine_us.model_api import *


class ky_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP regular heating assistance"
    documentation = (
        "Verified for FY2025 and FY2026. Earlier years use model parameter "
        "backfilling and are unverified historical estimates."
    )
    defined_for = "ky_liheap_eligible"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KY_BenefitMatrix_Heat-Cool_2026.xlsx",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/KY_BenefitMatrix_2025.xlsx",
        # Sections 2.4-2.6 (pages 8-9).
        "https://liheapch.acf.gov/docs/2026/state-plans/KY_Plan_2026.pdf#page=8",
        # Section 4(1).
        "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.liheap.payment
        income = spm_unit("ky_liheap_income", period) / MONTHS_IN_YEAR
        fpg = spm_unit("ky_liheap_fpg", period) / MONTHS_IN_YEAR
        size = spm_unit("spm_unit_size", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        # 921 KAR 4:116 Section 4(1)(e) lowers benefits for federally assisted
        # housing or receipt of a utility allowance. A household receiving a
        # utility allowance is already an assisted household.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        band = 0
        for rate in p.income_bands:
            band = band + (income > np.ceil(fpg * rate))
        income_points = where(
            subsidized,
            p.income_points.subsidized.calc(band),
            p.income_points.unsubsidized.calc(band),
        )
        fuel_points = p.fuel_points[fuel]
        coal_adjustment = (fuel == types.COAL) * p.coal_adjustment.calc(size)
        points = (
            min_(size, p.maximum_household_points)
            + income_points
            + fuel_points
            + coal_adjustment
        )
        # Reproduces every heating cell of the FY2026 "rev benefit income
        # range" and FY2025 "subsidy benefits" worksheets, including the
        # two-person coal exception and the reversed subsidized income points
        # that conflict with 921 KAR 4:116 Section 4(1)(c) (see
        # income_points/subsidized). The FY2026 sheet uses 2025 guidelines
        # despite its stale title and matches the plan's $15-$250 range; the
        # conditional "if no funding FFY26" sheet is not used.
        amount = np.ceil(points * p.dollars_per_point)
        amount = where(subsidized, np.ceil(amount * p.subsidized_housing_rate), amount)
        # Fuels without a published column (OTHER, SOLAR, UNSPECIFIED, NONE)
        # carry zero points, which also marks them as having no schedule. The
        # full seasonal subsidy may credit the account, so it is not capped at
        # the current bill.
        return where(fuel_points > 0, amount, 0)
