from openfisca_us.model_api import *


class biomass_fuel_property_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified biomass fuel property expenditures"
    documentation = "Expenditures for property—(i)which uses the burning of biomass fuel to heat a dwelling unit located in the United States and used as a residence by the taxpayer, or to heat water for use in such a dwelling unit, and (ii)which has a thermal efficiency rating of at least 75 percent (measured by the higher heating value of the fuel)."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25D#d_6"
