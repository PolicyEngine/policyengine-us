from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nh_fap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP actual-cost scheduled benefit"
    documentation = "Actual-cost scheduled intermediate before any heat-in-rent adjustment, not the final FAP award. Verified against the PY2027 schedule; earlier results are unverified historical estimates. Zero can mean that actual cost or fuel classification is unsupported, rather than legal ineligibility."
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=10, 17, 74, 76, 77, 78"
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
        expense = spm_unit("heating_expense", period)
        thresholds = p.payment.heating_cost_threshold
        cost_band = select(
            [expense < thresholds.CC, expense < thresholds.BB, expense < thresholds.AA],
            ["DD", "CC", "BB"],
            default="AA",
        )
        delivered_benefit = p.payment.delivered_benefit[cost_band][income_band]
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        utility = (heating_type == fuel.ELECTRICITY) | (
            heating_type == fuel.NATURAL_GAS
        )
        delivered = (
            (heating_type == fuel.FUEL_OIL)
            | (heating_type == fuel.PROPANE)
            | (heating_type == fuel.KEROSENE)
            | (heating_type == fuel.WOOD)
            | (heating_type == fuel.COAL)
        )
        multiplier = where(utility, p.payment.utility_multiplier, 1)
        # Half-up whole dollars reproduce every utility matrix cell.
        benefit = np.floor(delivered_benefit * multiplier + 0.5)
        # No heat-in-rent adjustment is inferred. Missing heated-room data
        # prevents the proxy route. Unknown, solar and other fuels have no
        # supported payment classification; zero marks an unsupported amount.
        # The schedule is not capped at the household's actual heating cost.
        return where((expense > 0) & (utility | delivered), benefit, 0)
