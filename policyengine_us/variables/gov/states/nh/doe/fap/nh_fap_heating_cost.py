from policyengine_us.model_api import *


class nh_fap_heating_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "New Hampshire FAP annual heating cost using actual or estimated cost"
    # PDF pages 17-18,76-77.
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=17"
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.doe.fap.heating_cost
        bedrooms = spm_unit.household("bedrooms", period)
        # Use bedrooms alone as an approved modeling approximation,
        # not the program's measured room count. No other rooms are inferred.
        # Zero bedrooms cannot distinguish a studio from missing information.
        rooms = max_(bedrooms, 0)
        # Whole-household bedrooms approximate the SPM unit's dwelling;
        # private, shared and business-only room adjustments are unobserved.
        dwelling = spm_unit("nh_fap_dwelling_type", period)
        county = spm_unit.household("county_str", period)
        # Preserve the existing county input's geographic fallback. Explicit
        # unknown/non-NH counties cannot establish an estimated heating cost.
        county_key = where(
            np.isin(county, list(p.heating_degree_days._children)),
            county,
            "UNAVAILABLE",
        )
        fuel = spm_unit("heating_type", period).decode_to_str()
        fuel_key = where(
            np.isin(fuel, list(p.fuel_cost_per_mbtu._children)),
            fuel,
            "UNAVAILABLE",
        )
        # WOOD approximates cordwood; pellets, bio-bricks and winter blends
        # cannot be distinguished with the existing heating type input.
        # The million divisor converts the heat-load quantity to MBTU.
        estimated_cost = (
            p.dwelling_factor[dwelling]
            * rooms
            * p.heating_degree_days[county_key]
            / 1_000_000
            * p.fuel_cost_per_mbtu[fuel_key]
            / p.fuel_efficiency[fuel_key]
        )
        actual_cost = max_(spm_unit("heating_expense", period), 0)
        # The schedule is monotonic in cost, so the higher cost yields the
        # better of the actual-cost and design-heat-load determinations.
        return max_(actual_cost, estimated_cost)
