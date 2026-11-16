from policyengine_us.model_api import *


class id_liheap_estimated_heating_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP estimated heating cost"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = "https://web.archive.org/web/20170127123014id_/http://www.healthandwelfare.idaho.gov/Portals/_Rainbow/Manuals/LIHEAP/Appendices/c_htgcost_matrix_PY07.pdf#page=1"

    def formula(spm_unit, period, parameters):
        area = spm_unit("id_liheap_heating_area", period)
        heating = spm_unit("heating_type", period)
        types = heating.possible_values
        p = parameters(period).gov.states.id.dhw.liheap.payment.estimated_heating_costs
        # PY2007 nine-month cost proxy; FY2026 applicability is unconfirmed.
        # Safe lookup leaves unknown areas unassigned after fuel selection.
        # No Idaho source names solar or kerosene. As in heating_expense, solar
        # reads as electric and kerosene as the chart's oil.
        lookup_area = clip(area, 1, 3)
        electric_provider = spm_unit("electricity_provider", period)
        gas_provider = spm_unit("natural_gas_provider", period)
        electric_providers = electric_provider.possible_values
        # As with the payment chart, blank historical combinations retain
        # the existing representative estimate instead of asserting zero cost.
        electric_cost = select(
            [
                (electric_provider == electric_providers.AVISTA) & (area < 3),
                (electric_provider == electric_providers.ROCKY_MOUNTAIN_POWER)
                & (area > 1),
            ],
            [
                p.electricity_avista[min_(lookup_area, 2)],
                p.electricity_rocky_mountain[max_(lookup_area, 2)],
            ],
            default=p.electricity[lookup_area],
        )
        gas_cost = where(
            (gas_provider == gas_provider.possible_values.AVISTA) & (area < 3),
            p.natural_gas_avista[min_(lookup_area, 2)],
            p.natural_gas[lookup_area],
        )
        cost = select(
            [
                (heating == types.ELECTRICITY) | (heating == types.SOLAR),
                heating == types.NATURAL_GAS,
                (heating == types.FUEL_OIL)
                | (heating == types.KEROSENE)
                | (heating == types.PROPANE),
                (heating == types.COAL) | (heating == types.WOOD),
            ],
            [
                electric_cost,
                gas_cost,
                p.oil_or_propane[lookup_area],
                p.coal_or_wood[lookup_area],
            ],
            default=0,
        )
        # Zero for unknown area or unsupported fuel is no modeled cost,
        # not a determination of legal ineligibility or actual heating costs.
        return where((area >= 1) & (area <= 3), cost, 0)
