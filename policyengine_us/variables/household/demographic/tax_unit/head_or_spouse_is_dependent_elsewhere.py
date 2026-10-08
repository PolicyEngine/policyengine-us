from policyengine_us.model_api import *


class head_or_spouse_is_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Head or spouse is a dependent elsewhere"
    documentation = (
        "Whether the head or the spouse of this tax unit is claimed as a "
        "dependent in another tax unit. Unlike head_is_dependent_elsewhere, "
        "this does not depend on which spouse is labelled head."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        claimed_on_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        filer = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.any(claimed_on_another_return & filer)
