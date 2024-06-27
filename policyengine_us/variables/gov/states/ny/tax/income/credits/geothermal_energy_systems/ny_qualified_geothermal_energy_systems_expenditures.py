from policyengine_us.model_api import *


class ny_qualified_geothermal_energy_systems_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York qualified geothermal energy systems expenditures"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (g)(2)(C)(9)(g-4)(2)
    defined_for = StateCode.NY
