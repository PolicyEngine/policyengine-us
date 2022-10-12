from policyengine_us.model_api import *


class energy_efficient_window_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Energy efficient window expenditures"
    documentation = "Expenditures on exterior windows (including skylights) that meet version 6.0 Energy Star program requirements."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25C#c_3_B",
        "https://www.law.cornell.edu/uscode/text/26/25C#c_2_B",
    )
