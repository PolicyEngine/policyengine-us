from openfisca_us.model_api import *


class irs_gross_income(Variable):
    value_type = float
    entity = Person
    label = "IRS gross income"
    unit = USD
    documentation = "Gross income as defined in the Internal Revenue Code"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/61"
