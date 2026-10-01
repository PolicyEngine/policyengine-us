from policyengine_us.model_api import *


class or_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP regular heating benefit"
    unit = USD
    defined_for = "or_liheap_eligible"
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=61,62,67,78,79,80,81,93,94"
    documentation = "Annual regular heating assistance, verified for FY2026. Earlier years use parameter backfilling and are unverified historical estimates. No actual-expense cap applies. Heat-in-rent households need the building heating fuel. Discretionary bulk-fuel minimum-delivery payments and local supplements are unsupported because the necessary award information is absent. Cooling, crisis and equipment assistance are excluded."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.payment
        region = max_(spm_unit("or_liheap_region", period), 1)
        size = clip(spm_unit("spm_unit_size", period), 1, p.max_payment_size)
        band = spm_unit("or_liheap_income_band", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        amount = select(
            [
                fuel == types.ELECTRICITY,
                fuel == types.FUEL_OIL,
                fuel == types.PROPANE,
                fuel == types.NATURAL_GAS,
                fuel == types.WOOD,
            ],
            [
                p.amount.electricity[region][size][band],
                p.amount.fuel_oil[size][band],
                p.amount.propane[size][band],
                p.amount.natural_gas[region][size][band],
                p.amount.wood[size][band],
            ],
            # No published column for unspecified, other, coal, kerosene or solar.
            default=0,
        )
        dwelling = spm_unit("or_liheap_dwelling_type", period)
        separate = dwelling == dwelling.possible_values.ROOMER_BOARDER_OWNER
        return amount * where(separate, p.roomer_rate, 1)
