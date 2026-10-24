from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nh_fap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire Fuel Assistance Program benefit"
    documentation = (
        "Modeled regular heating award using actual or bedroom-proxy heating cost. "
        "For unsubsidized heat included in rent, the model uses the ordinary fuel "
        "schedule without an additional reduction. This approved modeling assumption "
        "may overestimate awards: the state plan describes reduced heat-in-rent "
        "benefits but does not specify the calculation. Bedrooms alone approximate "
        "the program's room count. Verified against the PY2027 schedule; earlier "
        "results are unverified historical estimates. Zero can mean unsupported "
        "heating cost or fuel classification rather than legal ineligibility."
    )
    reference = (
        # PDF pages 10,17-21,57,74,76-78.
        "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=10",
        # FY2026 plan, section 2.3: heat-in-rent reduction remains unquantified.
        "https://liheapch.acf.gov/docs/2026/state-plans/NH_Plan_2026.pdf#page=8",
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
        # Half-up whole dollars reproduce every utility matrix cell.
        benefit = np.floor(delivered_benefit * multiplier + 0.5)
        # Approved approximation: unsubsidized heat-in-rent receives this
        # scheduled amount, including the fuel multiplier exactly once.
        # The state's heat-in-rent reduction remains unverified.
        # Unknown, solar and other fuels have no supported payment
        # classification; their zero multiplier marks an unsupported amount.
        # The schedule is not capped at the household's actual heating cost.
        return where(expense > 0, benefit, 0)
