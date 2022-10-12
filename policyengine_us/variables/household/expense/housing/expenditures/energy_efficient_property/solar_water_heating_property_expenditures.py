from policyengine_us.model_api import *


class solar_water_heating_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified solar water heating property expenditures"
    documentation = "Expenditures for property to heat water for use in a dwelling unit located in the United States and used as a residence by the taxpayer if at least half of the energy used by such property for such purpose is derived from the sun."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_1"
