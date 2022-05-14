from openfisca_us.model_api import *


class taxsim_year(Variable):
    value_type = int
    entity = TaxUnit
    label = "Policy year"
    documentation = "Tax year ending Dec 31(4 digits between 1960 and 2023, but state must be zero if year is before 1977. (We don't have code for state laws before 1977.) State tax laws are effectively inflated by 2.5%/year after 2021."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return period.start.year
