from policyengine_us.model_api import *


class every_filer_is_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Every head and spouse is a dependent elsewhere"
    documentation = (
        "Whether the tax unit has a head or spouse claimed as a dependent in "
        "another tax unit and none who is not. False for a tax unit with "
        "neither a head nor a spouse."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("head_or_spouse_is_dependent_elsewhere", period) & (
            tax_unit("head_spouse_count_not_dependent_elsewhere", period) == 0
        )
