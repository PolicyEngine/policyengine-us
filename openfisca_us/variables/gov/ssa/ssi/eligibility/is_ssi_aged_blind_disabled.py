from openfisca_us.model_api import *


class is_ssi_aged_blind_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is aged, blind, or disabled for the Supplemental Security Income program"
    label = "SSI aged, blind, or disabled"
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#a_1"

    formula = any_of_variables(["is_ssi_aged", "is_blind", "is_ssi_disabled"])
