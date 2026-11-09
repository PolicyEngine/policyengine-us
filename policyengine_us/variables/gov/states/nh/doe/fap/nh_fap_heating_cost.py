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
        # No room-count input exists, so bedrooms stand in for the room count.
        # Page 17 counts every room except hallways, unfinished basements,
        # garages, attics and closets, and the application form also counts
        # kitchen/dining and living/family rooms, so bedrooms understate rooms.
        # A dwelling has at least one room, so a studio or an unreported
        # bedroom count gets the one-room estimate. A homeless household has
        # no dwelling to heat and keeps its reported count.
        has_dwelling = ~spm_unit.household("is_homeless", period)
        rooms = max_(bedrooms, where(has_dwelling, 1, 0))
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
        # WOOD approximates cordwood; pellets and bio-bricks cannot be
        # distinguished with the existing heating type input. Winter blend, a
        # heating-oil blend, is entered as FUEL_OIL or KEROSENE, so its own
        # page 77 cost per MBTU is not used. An unsupported county or fuel
        # gives no estimate, whatever the room count.
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
