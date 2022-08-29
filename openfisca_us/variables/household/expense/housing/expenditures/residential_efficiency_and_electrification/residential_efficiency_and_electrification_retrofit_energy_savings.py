from openfisca_us.model_api import *


class retrofit_35_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on retrofits that achieve over 35 percent energy savings for households with an AMI over 80 percent"
    unit = USD
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587"
