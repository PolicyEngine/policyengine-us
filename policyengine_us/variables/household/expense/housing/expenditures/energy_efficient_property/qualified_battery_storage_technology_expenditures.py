from policyengine_us.model_api import *


class qualified_battery_storage_technology_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified battery storage technology expenditures"
    documentation = "Expenditures for qualified battery storage technology installed in connection with a dwelling unit located in the United States and used as a residence by the taxpayer and has the capacity not less than 3kwh."
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=352"
