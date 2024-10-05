from policyengine_us.model_api import *


class small_wind_energy_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified small wind energy property expenditures"
    documentation = "Expenditures for property which uses a wind turbine to generate electricity for use in connection with a dwelling unit located in the United States and used as a residence by the taxpayer."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_4"
