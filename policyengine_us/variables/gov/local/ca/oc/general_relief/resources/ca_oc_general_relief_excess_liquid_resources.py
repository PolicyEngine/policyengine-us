from policyengine_us.model_api import *


class ca_oc_general_relief_excess_liquid_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief excess liquid resources"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2023-04/GR%20Reg%20SECTION%2060%20-%20Approved%20-%20March%202023_0.pdf#page=01"

    def formula(spm_unit, period, parameters):
        # NOTE: amount available to reduce an initial-month grant; the ordinary
        # monthly payment is not modeled because Orange County's MAP schedule
        # is not publicly available.
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        liquid_resources = spm_unit("spm_unit_cash_assets", period)
        return max_(liquid_resources - p.liquid_resource_disregard, 0)
