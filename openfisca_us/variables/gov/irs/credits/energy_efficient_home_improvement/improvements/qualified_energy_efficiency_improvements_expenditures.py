from openfisca_us.model_api import *


class qualified_energy_efficiency_improvements_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Expenditures on qualified energy efficiency improvements"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/25C#c",
        "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340",
    )

    formula = sum_of_variables(
        "gov.irs.credits.residential_energy.nonbusiness.qualified_expenditures.energy_efficiency_improvements"
    )
