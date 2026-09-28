from policyengine_us.model_api import *


class ks_liheap_energy_vulnerable(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP household meets heating cost responsibility rules"
    documentation = "Defaults to separately paid heating costs or heat included in unsubsidized rent. Set this fact directly for shared unmetered heat, subsidized tenants paying excess heating charges, limited FHA subsidies, or homeless households owing qualifying heating debt from a prior Kansas address. The default assumes an adult household member is responsible for separately metered purchased fuel."
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm13300.htm"

    def formula(spm_unit, period, parameters):
        pays_for_heat = spm_unit("has_heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        return pays_for_heat | (heat_in_rent & ~subsidized)
