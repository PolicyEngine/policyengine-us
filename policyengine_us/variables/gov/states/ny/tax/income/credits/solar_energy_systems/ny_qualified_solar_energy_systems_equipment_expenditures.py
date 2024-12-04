from policyengine_us.model_api import *


class ny_qualified_solar_energy_systems_equipment_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified solar energy systems equipment expenditures in New York"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (g)(2)(C)(9)(g-1)(2)
    defined_for = StateCode.NY
