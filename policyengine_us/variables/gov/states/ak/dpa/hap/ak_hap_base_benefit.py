from policyengine_us.model_api import *


class ak_hap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska HAP base benefit before sharing and utility allowance adjustments"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3002/3002-1_households.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/addendum/addendum_a.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
        "https://cchrc.org/wp-content/uploads/media/Consumer_Guide_Home_Heating.pdf#page=23",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.hap.benefit
        place = spm_unit.household("place_fips", period)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        oil_table = p.community_points.oil
        gas_table = p.community_points.natural_gas
        oil_place = where(
            np.isin(place, list(oil_table._children)), place, "UNAVAILABLE"
        )
        gas_place = where(
            np.isin(place, list(gas_table._children)), place, "UNAVAILABLE"
        )
        oil_fuel = (
            (fuel == fuels.FUEL_OIL)
            | (fuel == fuels.KEROSENE)
            | (fuel == fuels.PROPANE)
            | (fuel == fuels.ELECTRICITY)
        )
        wood_or_coal = (fuel == fuels.WOOD) | (fuel == fuels.COAL)
        # Propane uses oil points under 7 AAC 44.080(f). Kerosene is Grade 1
        # heating oil in the AHFC-funded technical guide. Unclassified OTHER
        # fuels and unmatched oil geography yield unavailable modeled amounts
        # (zero fallback), not statutory denials. Anchorage
        # oil is ambiguous. The gas table uses a documented nearest-community
        # approximation where a direct published place match is unavailable.
        # Purchased wood/coal is the approved modeling default. Existing
        # heating_type cannot identify self-harvest or pellets, whose factors
        # differ; neither subtype is inferred from the reported expense.
        community_points = select(
            [oil_fuel, fuel == fuels.NATURAL_GAS, wood_or_coal],
            [
                oil_table[oil_place],
                gas_table[gas_place],
                oil_table[oil_place] * p.purchased_wood_coal_multiplier,
            ],
            default=0,
        )
        dwelling = spm_unit("ak_hap_dwelling_type", period)
        # Restore the table's decimal tenths after float32 storage so exact
        # half points retain the manual's half-up rounding below.
        factor = np.round(
            spm_unit("ak_hap_income_factor", period).astype(np.float64), 1
        )
        person = spm_unit.members
        age = person("age", period)
        # Existing disability status approximates the manual's documented
        # disability categories. Excluded members cannot add priority points.
        vulnerable = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
            & (
                (age >= p.elderly_age)
                | (age < p.child_age_limit)
                | person("is_disabled", period)
            )
        )
        points = community_points * p.dwelling_factor[dwelling] * factor
        points = points + vulnerable * p.vulnerability_points
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        # Full annual rent satisfies the expense test for nonsubsidized
        # heat-in-rent households. Pre-subsidy rent avoids benefit feedback.
        expense = where(
            heat_in_rent,
            add(spm_unit, period, ["pre_subsidy_rent"]),
            spm_unit("heating_expense", period),
        )
        # The table identifies all-resident tribal routing. Native-only tribal
        # eligibility and contrary interagency arrangements are unobserved;
        # never infer tribal enrollment from race. Finer residency, temporary
        # shelter duration and vendor-credit rules are also unobserved.
        state_served = ~np.isin(place, p.tribal_service_places)
        eligible = (
            (factor > 0)
            & (community_points > 0)
            & (expense > p.minimum_expense)
            & ~(heat_in_rent & subsidized)
            & state_served
            & (points >= p.minimum_points)
        )
        # Apply the unrounded minimum before half-up whole-point rounding.
        # This is the sole-household base amount, without an expense cap.
        # ak_hap applies sharing and utility-allowance reductions to dollars
        # under the approved manual-based modeling convention.
        rounded_points = min_(np.floor(points + 0.5), p.maximum_points)
        return where(eligible, rounded_points * p.point_value, 0)
