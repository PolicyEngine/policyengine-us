from policyengine_us.model_api import *


class head_spouse_count_not_dependent_elsewhere(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Head and spouse count not dependent elsewhere"
    documentation = (
        "Number of tax unit heads and spouses who are not claimed as a "
        "dependent in another tax unit."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        claimed_on_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        filer = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(filer & ~claimed_on_another_return)
