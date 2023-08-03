from policyengine_us.model_api import *


class solar_electric_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified solar electric property expenditures"
    documentation = "Expenditures for property which uses solar energy to generate electricity for use in a dwelling unit located in the United States and used as a residence by the taxpayer."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_2"
