from openfisca_us.model_api import *


class residential_efficiency_electrification_retrofit_energy_savings(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modeled energy system savings from a residential efficiency and electrification retrofit"
    documentation = "In kilowatt hours per month. Do not include savings from projects listed in other electrification and efficiency expenditure categories."
    unit = "kWh/month"
    definition_period = YEAR
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587"
