from openfisca_us.model_api import *


class specified_possession_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income from Guam, American Samoa, or the Northern Mariana Islands"
    unit = USD
    documentation = "Income generated in the above territories by any individual who is a bona fide resident."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/931"
