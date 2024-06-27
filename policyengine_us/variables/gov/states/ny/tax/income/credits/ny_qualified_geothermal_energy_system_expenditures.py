from policyengine_us.model_api import *


class ny_qualified_geothermal_energy_system_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified geothermal energy system equipment expenditures"
    documentation = "Money spent in the current year for the purchase or lease of geothermal energy system equipment."
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # PART 1 (g)(2)(C)(9)(g-4)
    defined_for = StateCode.NY
