from openfisca_us.model_api import *


class energy_efficient_insulation_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Energy efficient insulation expenditures"
    documentation = "Expenditures on any insulation material or system which is specifically and primarily designed to reduce the heat loss or gain of a dwelling unit when installed in or on such dwelling unit."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#c_3_A"
