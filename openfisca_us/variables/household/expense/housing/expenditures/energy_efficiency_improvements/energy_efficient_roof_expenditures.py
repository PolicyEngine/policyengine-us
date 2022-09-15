from openfisca_us.model_api import *


class energy_efficient_roof_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Energy efficient roof expenditures"
    documentation = "Expenditures on metal or asphalt roof or roof products that meet Energy Star program requirements and have appropriate pigmented coatings or cooling granules which are specifically and primarily designed to reduce the heat gain of such dwelling unit."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25C#c_2_A",
        "https://www.law.cornell.edu/uscode/text/26/25C#c_3_A",
    )
