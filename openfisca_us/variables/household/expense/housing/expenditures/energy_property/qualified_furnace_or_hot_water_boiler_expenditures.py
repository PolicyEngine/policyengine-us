from openfisca_us.model_api import *


class qualified_furnace_or_hot_water_boiler_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on qualified natural gas, propane, or oil furnaces or hot water boilers"
    documentation = "Must achieve an annual fuel utilization efficiency rate of not less than 95."
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25C#d_4"
