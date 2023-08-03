from policyengine_us.model_api import *


class residential_efficiency_electrification_retrofit_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on efficiency and electrification retrofits "
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587"
