from openfisca_us.model_api import *


class property_tax_primary_residence(Variable):
    value_type = float
    entity = Person
    label = "Property tax for the real estate that includes the principal residence"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(["property_tax_primary_residence"])