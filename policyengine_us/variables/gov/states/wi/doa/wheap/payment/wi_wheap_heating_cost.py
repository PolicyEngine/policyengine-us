from policyengine_us.model_api import *


class wi_wheap_heating_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wisconsin WHEAP benefit heating cost"
    defined_for = StateCode.WI
    reference = (
        # Section 2.3.1 and sections 4.4.17 and 4.4.28.2-4.4.28.3.
        # PDF pages 26-27, 79, 86-87
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=26",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WI_BenefitMatrix_2026.xlsx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.doa.wheap.payment
        dwelling = spm_unit("wi_wheap_dwelling_type", period)
        dwelling_types = dwelling.possible_values
        # Bedrooms approximate the room count, which also includes kitchens
        # and living rooms. HE+ accepts 1 to 9 rooms (section 4.4.17; the
        # calculator's Benefits!C12 rejects 0), so a studio counts one room.
        # Motels and campers count one room.
        bedrooms = spm_unit.household("bedrooms", period)
        rooms = where(
            dwelling == dwelling_types.MOTEL_OR_CAMPER,
            1,
            clip(bedrooms, 1, p.proxy.max_rooms),
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        is_electricity = heating_type == fuel.ELECTRICITY
        # Kerosene, coal and other fuels use the wood-or-other row. Solar has
        # no fuel record and is unsupported.
        fuel_classes = [
            heating_type == fuel.FUEL_OIL,
            heating_type == fuel.NATURAL_GAS,
            heating_type == fuel.PROPANE,
            is_electricity,
            (heating_type == fuel.WOOD)
            | (heating_type == fuel.KEROSENE)
            | (heating_type == fuel.COAL)
            | (heating_type == fuel.OTHER),
        ]
        base = select(
            fuel_classes,
            [
                p.proxy.base.fuel_oil[dwelling],
                p.proxy.base.natural_gas[dwelling],
                p.proxy.base.propane[dwelling],
                p.proxy.base.electricity[dwelling],
                p.proxy.base.wood_other[dwelling],
            ],
            default=0,
        )
        per_room = select(
            fuel_classes,
            [
                p.proxy.per_room.fuel_oil[dwelling],
                p.proxy.per_room.natural_gas[dwelling],
                p.proxy.per_room.propane[dwelling],
                p.proxy.per_room.electricity[dwelling],
                p.proxy.per_room.wood_other[dwelling],
            ],
            default=0,
        )
        proxy = base + per_room * rooms
        # An electric heating bill also covers non-heating use.
        reported = spm_unit("heating_expense", period)
        baseload = where(is_electricity, reported * p.electric_baseload_rate, 0)
        eligible_cost = max_(reported - baseload, 0)
        lower = p.proxy.floor_rate * proxy
        upper = p.proxy.cap_rate * proxy
        # Shared and business meters also use the proxy floor but cannot be
        # identified from existing inputs.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        cost = where(
            heat_in_rent | (eligible_cost <= 0),
            lower,
            clip(eligible_cost, lower, upper),
        )
        supported = np.any(fuel_classes, axis=0)
        return where(supported, cost, 0)
