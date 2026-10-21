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
        lookup_area = clip(area, 1, 3)
        cost = select(
            [
                heating == types.ELECTRICITY,
                heating == types.NATURAL_GAS,
                (heating == types.FUEL_OIL) | (heating == types.PROPANE),
                (heating == types.COAL) | (heating == types.WOOD),
            ],
            [
                p.electricity[lookup_area],
                p.natural_gas[lookup_area],
                p.oil_or_propane[lookup_area],
                p.coal_or_wood[lookup_area],
            ],
            default=0,
        )
        # Zero for unknown area or unsupported fuel is no modeled cost,
        # not a determination of legal ineligibility or actual heating costs.
        return where((area >= 1) & (area <= 3), cost, 0)
