from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nh_fap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire Fuel Assistance Program benefit"
    documentation = (
        "Regular heating award from the PY2027 schedule, using the larger of the "
        "actual heating cost and the heating-cost estimate, with bedrooms (at "
        "least one room for a dwelling) standing in for the room count. "
        "Unsubsidized heat included in rent receives 0.625 of the scheduled "
        "amount. The FY2026 and FY2027 state plans (item 2.3, page 8) say these "
        "renters' 'benefits are reduced', but no document for either year prints "
        "the rate. The PY2025 manual printed heat-in-rent matrices at 0.625 of "
        "its ordinary ones (page 74); the PY26 benefit matrix and the PY2027 "
        "schedule (page 78) print none. The rate is inferred from each plan's "
        "minimum benefit (item 2.6, page 9), which is the schedule's lowest cell "
        "times 0.625: $100 for FY2026 (160 x 0.625) and $188 for FY2027 "
        "(300 x 0.625, rounded up). Elsewhere on page 9, the FY2027 plan says "
        "these renters are 'eligible for a benefit' where the FY2026 plan said "
        "'eligible for a reduced benefit'. Period 2026 uses the PY26 chart's "
        "benefit amounts and heating cost tiers and keeps the PY2027 "
        "heating-cost estimate, because the PY26 heating cost tables are not "
        "published. Verified against the PY2027 schedule; period 2026 beyond the "
        "PY26 chart and earlier results are unverified historical estimates. "
        "Zero can mean an unsupported heating cost or fuel classification rather "
        "than legal ineligibility."
    )
    reference = (
        # PDF pages 10,17-21,57,74,76-78.
        "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=10",
        # FY2026 plan, PDF pages 8-9: items 2.3 and 2.6.
        "https://liheapch.acf.gov/docs/2026/state-plans/NH_Plan_2026.pdf#page=8",
        # PY2025 manual, Wayback Machine capture: heat-in-rent matrices.
        "https://web.archive.org/web/20250523173906/https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=74",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/NH_BenefitMatrix_2026.pdf#page=1",
        # FY2027 plan, PDF pages 8-9: items 2.3 and 2.6.
        "https://liheapch.acf.gov/docs/2027/state-plans/NH_Plan_2027.pdf#page=8",
    )
    defined_for = "nh_fap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap
        size = spm_unit("nh_fap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        # Use the guideline at the start of the modeled heating season.
        # Within-season February guideline changes are not separately modeled.
        poverty_guideline = fpg(
            size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        income = spm_unit("nh_fap_countable_income", period)
        bounds = p.payment.income_band_upper_bound
        income_band = select(
            [
                income <= poverty_guideline * bounds.A,
                income <= poverty_guideline * bounds.B,
                income <= poverty_guideline * bounds.C,
                income <= poverty_guideline * bounds.D,
                income <= poverty_guideline * bounds.E,
            ],
            ["A", "B", "C", "D", "E"],
            default="F",
        )
        expense = spm_unit("nh_fap_heating_cost", period)
        thresholds = p.payment.heating_cost_threshold
        cost_band = select(
            [expense < thresholds.CC, expense < thresholds.BB, expense < thresholds.AA],
            ["DD", "CC", "BB"],
            default="AA",
        )
        delivered_benefit = p.payment.delivered_benefit[cost_band][income_band]
        heating_type = spm_unit("heating_type", period)
        multiplier = p.payment.benefit_multiplier[heating_type]
        # Rounding up to whole dollars reproduces every utility matrix cell
        # of the PY26 chart and the PY2027 schedule. Both multipliers are
        # exact binary fractions, so the product carries no rounding error.
        benefit = np.ceil(delivered_benefit * multiplier)
        # The FY2026 and FY2027 plans reduce the award when heat is included
        # in rent (see the documentation). The reduction applies to the
        # whole-dollar scheduled amount, as the PY2025 manual's heat-in-rent
        # tables did, and rounds up again. Only the plans' minimum benefits
        # confirm a heat-in-rent amount: $100 for FY2026 (160 * 0.625) and
        # $188 for FY2027 (300 * 0.625 = 187.5). The rounding of the other
        # heat-in-rent amounts is unverified.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heat_in_rent_benefit = np.ceil(benefit * p.payment.heat_in_rent_multiplier)
        benefit = where(heat_in_rent, heat_in_rent_benefit, benefit)
        # Unspecified and other fuels have no page 77 row; their zero
        # multiplier marks an unsupported amount.
        # The schedule is not capped at the household's actual heating cost.
        return where(expense > 0, benefit, 0)
