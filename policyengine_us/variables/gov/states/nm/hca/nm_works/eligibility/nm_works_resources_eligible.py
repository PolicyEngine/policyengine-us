from policyengine_us.model_api import *


class nm_works_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works resources eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0510.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.510.8 NMAC, resources/property limits:
        # - Liquid resources must not exceed $1,500
        # - Non-liquid resources must not exceed $2,000
        # PolicyEngine currently models liquid financial assets explicitly but does
        # not yet distinguish countable non-liquid property from exempt home equity
        # or exempt transportation vehicles under 8.102.510.10 NMAC. Applying
        # assessed_property_value or household_vehicles_value directly here would
        # overstate countable non-liquid resources for many households, so this
        # check enforces the directly modeled liquid-resource test only.
        p = parameters(period).gov.states.nm.hca.nm_works.resources.limit
        liquid_resources = spm_unit("spm_unit_cash_assets", period.this_year)
        return liquid_resources <= p.liquid
