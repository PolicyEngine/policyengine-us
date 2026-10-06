from policyengine_us.model_api import *


class limited_capital_loss_person(Variable):
    value_type = float
    entity = Person
    label = "Limited capital loss deduction for each person"
    unit = USD
    documentation = (
        "Each head's or spouse's part of the tax unit's net capital loss "
        "deduction after the Section 1211(b) limit (limited_capital_loss), in "
        "proportion to their own net capital losses. A tax unit dependent's "
        "capital losses are on their own return, so their part is zero."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1211#b"

    def formula(person, period, parameters):
        capital_share = filer_share(person, period, person("capital_losses", period))
        return person.tax_unit("limited_capital_loss", period) * capital_share
