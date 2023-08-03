from policyengine_us.model_api import *


class air_sealing_ventilation_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on air sealing and ventilation"
    unit = USD
    definition_period = YEAR
    # NB: Combined with insulation expenditures for the rebate.
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585"
