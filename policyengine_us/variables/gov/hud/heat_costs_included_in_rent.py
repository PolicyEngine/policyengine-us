from policyengine_us.model_api import *


class heat_costs_included_in_rent(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether household's heating costs are included in the rent payments"
    definition_period = YEAR
    # Excludes other types of utilities
    reference = "https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm"
