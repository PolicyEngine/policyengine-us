from policyengine_us.model_api import *


def ak_hap_award(spm_unit, period, parameters, share, apply_utility_allowance):
    # 7 AAC 44.080: community points (a)-(f) times the dwelling factor (g),
    # reduced to the dwelling share (h), times the income factor (i), plus
    # the vulnerable point (k), halved for a utility allowance (l), then the
    # 2.0-point minimum (m), half-up rounding (n) and the 35-point cap (o).
    p = parameters(period).gov.states.ak.dpa.hap.benefit
    place = spm_unit.household("place_fips", period)
    zip_code = spm_unit.household("zip_code", period)
    county = spm_unit.household("county_str", period)
    fuel = spm_unit("heating_type", period)
    fuels = fuel.possible_values
    # Addendum A assigns points by community. A listed Census place is the
    # closest match. A household without one takes the points of its ZIP
    # code's largest community, and otherwise the most common points of its
    # borough or census area. The oil and gas tables share their keys. The
    # shared county variable supplies the state's first county when none is
    # sent.
    place_listed = np.isin(place, list(p.community_points.oil))
    place_key = where(place_listed, place, "UNAVAILABLE")
    zip_listed = ~place_listed & np.isin(zip_code, list(p.zip_code_points.oil))
    zip_key = where(zip_listed, zip_code, "UNAVAILABLE")
    county_listed = np.isin(county, list(p.county_points.oil))
    county_key = where(county_listed, county, "UNAVAILABLE")
    oil_points = select(
        [place_listed, zip_listed],
        [p.community_points.oil[place_key], p.zip_code_points.oil[zip_key]],
        default=p.county_points.oil[county_key],
    )
    gas_points = select(
        [place_listed, zip_listed],
        [
            p.community_points.natural_gas[place_key],
            p.zip_code_points.natural_gas[zip_key],
        ],
        default=p.county_points.natural_gas[county_key],
    )
    # 7 AAC 44.080(f) and grant step 1 put electricity, propane, steam, hot
    # water and vehicle gasoline on oil points. OTHER stands for the steam,
    # hot-water and vehicle-gasoline cases, which heating_type cannot name,
    # and a SOLAR household's bill is grid electricity. Kerosene is Grade 1
    # heating oil in the AHFC-funded technical guide.
    oil_fuel = (
        (fuel == fuels.FUEL_OIL)
        | (fuel == fuels.KEROSENE)
        | (fuel == fuels.PROPANE)
        | (fuel == fuels.ELECTRICITY)
        | (fuel == fuels.SOLAR)
        | (fuel == fuels.OTHER)
    )
    # WOOD and COAL take the purchased-fuel factor of 7 AAC 44.080(d);
    # heating_type cannot identify self-harvested fuel or pellets, whose
    # factors differ under (c) and (e).
    wood_or_coal = (fuel == fuels.WOOD) | (fuel == fuels.COAL)
    # A household with no listed place, no listed ZIP code and no Alaska
    # borough has no points.
    community_points = select(
        [oil_fuel, fuel == fuels.NATURAL_GAS, wood_or_coal],
        [
            oil_points,
            gas_points,
            oil_points * p.purchased_wood_coal_multiplier,
        ],
        default=0,
    )
    dwelling = spm_unit("ak_hap_dwelling_type", period)
    # Restore the table's decimal tenths after float32 storage so exact
    # half points retain the half-up rounding below.
    factor = np.round(spm_unit("ak_hap_income_factor", period).astype(np.float64), 1)
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
    heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
    subsidized = spm_unit("receives_housing_assistance", period) | spm_unit.household(
        "is_in_public_housing", period
    )
    # Subsidized households paying heat directly receive a HUD utility
    # allowance for tenant-paid utilities (24 CFR 965.502(a) and
    # 982.517(a)(1)), so 44.080(l) applies without a reported allowance.
    # Step-down programs that end the allowance after a year are unobserved.
    utility_allowance = apply_utility_allowance & subsidized & ~heat_in_rent
    points = community_points * p.dwelling_factor[dwelling] * share * factor
    points = points + vulnerable * p.vulnerability_points
    points = points * where(utility_allowance, 1 - p.utility_allowance_reduction, 1)
    # NOTE: Drop floating-point noise from fractional shares so exact
    # half points and the 2.0 minimum compare exactly.
    points = np.round(points, 9)
    # Full annual rent satisfies the expense test for nonsubsidized
    # heat-in-rent households. Pre-subsidy rent avoids benefit feedback.
    expense = where(
        heat_in_rent,
        add(spm_unit, period, ["pre_subsidy_rent"]),
        spm_unit("heating_expense", period),
    )
    # The lists identify all-resident tribal routing by the same key that
    # supplies the points: place, then ZIP code, then borough. Native-only
    # tribal eligibility and contrary interagency arrangements are
    # unobserved; never infer tribal enrollment from race. Finer residency,
    # temporary shelter duration and vendor-credit rules are also unobserved.
    tribe_served = select(
        [place_listed, zip_listed],
        [
            np.isin(place, p.tribal_service_places),
            np.isin(zip_code, p.tribal_service_zip_codes),
        ],
        default=np.isin(county, p.tribal_service_counties),
    )
    # 7 AAC 44.040(b)(3)(B) excludes households residing on a military base.
    # Census draws the listed places from the installations themselves, and
    # Addendum A prints the listed ZIP codes beside them. Either marks a
    # household, since some bases have no place and others share a ZIP code.
    on_base = np.isin(place, p.military_base_places) | np.isin(
        zip_code, p.military_base_zip_codes
    )
    eligible = (
        (factor > 0)
        & (community_points > 0)
        & (expense > p.minimum_expense)
        & ~(heat_in_rent & subsidized)
        & ~tribe_served
        & ~on_base
        & (points >= p.minimum_points)
    )
    rounded_points = min_(np.floor(points + 0.5), p.maximum_points)
    return where(eligible, rounded_points * p.point_value, 0)


class ak_hap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alaska HAP base benefit before sharing and utility allowance adjustments"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3002/3002-1_households.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3007/3007-1_subsidized_heat_and_application_processing.htm",
        "http://dpaweb.hss.state.ak.us/manuals/HAP/addendum/addendum_a.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
        "https://cchrc.org/wp-content/uploads/media/Consumer_Guide_Home_Heating.pdf#page=23",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # The award as if the household were the sole household in the
        # dwelling (7 AAC 44.035(c)), without the utility-allowance reduction.
        return ak_hap_award(spm_unit, period, parameters, 1, False)
