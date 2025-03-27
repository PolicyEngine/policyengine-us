from policyengine_us.model_api import *


class heating_costs_included_in_rent(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Household's heating costs are included in the rent amount"
    definition_period = YEAR
    # Excludes other types of utilities
    reference = "https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm#OR"
