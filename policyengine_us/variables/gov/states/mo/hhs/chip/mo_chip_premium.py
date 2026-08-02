from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mo_chip_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri MO HealthNet for Kids annual CHIP premium"
    unit = USD
    documentation = (
        "Annual Missouri MO HealthNet for Kids (separate CHIP) premium "
        "paid by the tax unit. The state sets one household-level monthly "
        "premium that varies by both family size and three FPL tiers, "
        "assigned by comparing monthly income to the Appendix E chart's "
        "dollar boundaries: each FPL percentage converted to monthly "
        "dollars and rounded up to the next whole dollar."
    )
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://mydss.mo.gov/childrens-health-insurance-program-chip-premium-chart",
        "https://dssmanuals.mo.gov/wp-content/uploads/2019/05/appendix-e.pdf",
    )

    def formula(tax_unit, period, parameters):
        has_chip_member = add(tax_unit, period, ["is_chip_eligible"]) > 0
        income_level = tax_unit("tax_unit_medicaid_income_level", period)
        family_size = tax_unit("tax_unit_size", period)
        pregnant_count = add(tax_unit, period, ["current_pregnancies"])
        state_group = tax_unit.household("state_group_str", period)
        # tax_unit_medicaid_income_level divides income by an FPG that
        # counts children a pregnant member is expected to deliver;
        # multiply by that same FPG to recover monthly dollar income.
        income_fpg = fpg(family_size + pregnant_count, state_group, period, parameters)
        # Missouri keys the Appendix E chart on the CHIP child's MAGI
        # household size, which counts a pregnant member as one person -
        # the unborn child counts only in the pregnant member's own
        # household (DSS manual 1885.010.00 household example).
        monthly_fpg = fpg(family_size, state_group, period, parameters) / MONTHS_IN_YEAR
        p = parameters(period).gov.states.mo.hhs.chip.premium
        # The Appendix E chart sets each tier boundary at the FPL percentage
        # converted to monthly dollars and rounded up to the next whole
        # dollar; income at the published boundary falls in the lower tier,
        # and the tier 1 floor itself is charged the tier 1 premium.
        # Products are rounded to cents before the ceiling to avoid float
        # error tipping exact whole-dollar boundaries upward.
        tier_1_floor = np.ceil(np.round(monthly_fpg * p.fpl_floor.tier_1, 2))
        tier_2_floor = np.ceil(np.round(monthly_fpg * p.fpl_floor.tier_2, 2))
        tier_3_floor = np.ceil(np.round(monthly_fpg * p.fpl_floor.tier_3, 2))
        monthly_income = np.round(income_level * income_fpg / MONTHS_IN_YEAR, 2)
        monthly_premium = select(
            [
                monthly_income > tier_3_floor,
                monthly_income > tier_2_floor,
                monthly_income >= tier_1_floor,
            ],
            [
                p.tier_3.calc(family_size),
                p.tier_2.calc(family_size),
                p.tier_1.calc(family_size),
            ],
            default=0,
        )
        return has_chip_member * monthly_premium * MONTHS_IN_YEAR
