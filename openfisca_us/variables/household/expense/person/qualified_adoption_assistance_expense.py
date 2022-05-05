from openfisca_us.model_api import *


class qualified_adoption_assistance_expense(Variable):
    value_type = float
    entity = Person
    label = "Qualified adoption expense"
    unit = USD
    definition_period = YEAR
    documentation = "Qualified adoption expense (as defined in 26 U.S. Code § 23(d)) made pursuant to an adoption assistance program."
    reference = "https://www.law.cornell.edu/uscode/text/26/23#d"

    # Note that this is an above-the-line deduction. There is more
    # generous tax relief for qualified adoption expenses involving
    # children with special needs, which is not modelled here.
