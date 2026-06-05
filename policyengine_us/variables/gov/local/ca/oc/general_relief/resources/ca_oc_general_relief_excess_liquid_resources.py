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
        # Liquid resources over the $50 disregard count as income (Sec 70.2.g)
        # and reduce the initial-month grant (Sec 60.2.a); this feeds
        # ca_oc_general_relief_countable_income. Modeled as a single month's
        # income, which zeroes the grant when the balance exceeds the monthly
        # maximum aid payment; the multi-month period of ineligibility in
        # Sec 70.2.r is not separately tracked.
        p = parameters(period).gov.local.ca.oc.general_relief.resources
        liquid_resources = spm_unit("spm_unit_cash_assets", period)
        return max_(liquid_resources - p.liquid_resource_disregard, 0)
