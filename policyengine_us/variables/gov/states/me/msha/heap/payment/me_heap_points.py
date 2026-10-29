from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.me.msha.heap.payment.me_heap_income_multiplier import (
    FLOAT_GUARD_DECIMALS,
)


class me_heap_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Maine HEAP benefit points"
    defined_for = StateCode.ME
    reference = (
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ME_BenefitMatrix_2026.pdf#page=1",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        # PDF pages 15-17
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=15",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.me.msha.heap.points
        dwelling_points = p.dwelling[spm_unit("me_heap_dwelling_type", period)]
        # A county outside the table, such as UNKNOWN or a county in another
        # state, gets no county points. The formula runs for every household
        # before defined_for applies, and the lookup raises on an unlisted key,
        # so those counties read a listed key and are then zeroed.
        county = spm_unit.household("county_str", period)
        in_table = np.isin(county, list(p.county))
        listed_county = where(in_table, county, next(iter(p.county)))
        county_points = where(in_table, p.county[listed_county], 0)
        # WOOD is the cordwood row. SOLAR stands for a grid-tied home with
        # electric heat. OTHER (pellets, corn, bio-fuel, biobricks) is
        # eligible and scores no fuel points, since those rows have no
        # heating_type value; NONE and UNSPECIFIED have no row.
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        fuel_points = select(
            [
                (fuel == fuels.ELECTRICITY) | (fuel == fuels.SOLAR),
                fuel == fuels.PROPANE,
                fuel == fuels.KEROSENE,
                fuel == fuels.FUEL_OIL,
                fuel == fuels.COAL,
                fuel == fuels.NATURAL_GAS,
                fuel == fuels.WOOD,
            ],
            [
                p.fuel.electricity,
                p.fuel.lp_gas,
                p.fuel.kerosene,
                p.fuel.oil,
                p.fuel.coal,
                p.fuel.natural_gas,
                p.fuel.wood,
            ],
            default=0,
        )
        # Priority points are awarded once per household, for any member.
        person = spm_unit.members
        age = person("age", period)
        priority = p.priority
        at_risk = (
            (age >= priority.elderly_age)
            | person("is_disabled", period)
            | (age <= priority.young_child_age)
        )
        older_child = (age > priority.young_child_age) & (
            age < priority.child_age_limit
        )
        priority_points = select(
            [spm_unit.any(at_risk), spm_unit.any(older_child)],
            [priority.amount, priority.older_child_amount],
            default=0,
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        subsidized_points = where(subsidized & ~heat_in_rent, p.subsidized_heating, 0)
        raw_points = (
            p.base
            + dwelling_points
            + county_points
            + fuel_points
            + priority_points
            + subsidized_points
        )
        # Points are adjusted by the income multiplier and prorated by the
        # share of members who are eligible, then fractions are rounded up.
        multiplier = spm_unit("me_heap_income_multiplier", period)
        eligible_share = spm_unit("me_heap_household_size", period) / (
            spm_unit.nb_persons()
        )
        adjusted_points = raw_points * multiplier * eligible_share
        return np.ceil(np.round(adjusted_points, FLOAT_GUARD_DECIMALS))
