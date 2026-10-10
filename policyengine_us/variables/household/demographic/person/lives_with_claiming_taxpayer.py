from policyengine_us.model_api import *


class lives_with_claiming_taxpayer(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Lives with the taxpayer who can claim them as a dependent"
    documentation = (
        "Whether, for more than half the year, the person's principal place "
        "of residence was the home of the taxpayer who can claim them as a "
        "dependent (see claimed_as_dependent_on_another_return). Rules read "
        "it only for a person who can be claimed."
    )
    reference = ("https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=25",)
