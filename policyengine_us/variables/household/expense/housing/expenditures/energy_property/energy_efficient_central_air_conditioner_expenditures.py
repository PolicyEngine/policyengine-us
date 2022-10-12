from policyengine_us.model_api import *


class energy_efficient_central_air_conditioner_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    label = "Expenditures on energy efficient central air conditioners"
    # Before the Inflation Reduction Act, these had to be the highest
    # efficiency tier established by the Consortium for Energy Efficiency as
    # of 2009.
    # After the Inflation Reduction Act, they had to be the highest efficiency
    # tier (not including any advanced tier) established by the Consortium for
    # Energy Efficiency as of the beginning of the calendar year in which the
    # property is placed in service.
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25C#d_3_C",
        "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=342",
    )
