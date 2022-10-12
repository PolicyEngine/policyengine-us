from policyengine_us.model_api import *


class electric_stove_cooktop_range_or_oven_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on electric stoves, cooktop ranges, or ovens"
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585"
