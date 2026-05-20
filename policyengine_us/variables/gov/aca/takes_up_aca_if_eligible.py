from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up ACA"
    definition_period = YEAR
    default_value = True
    documentation = (
        "Whether the tax unit takes up Marketplace coverage when otherwise "
        "eligible. Reported Marketplace coverage at interview is treated as "
        "observed take-up; otherwise take-up follows the data-supplied or "
        "simulated take-up switch."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        reported_marketplace_coverage = tax_unit.any(
            person("has_marketplace_health_coverage_at_interview", period)
        )
        simulated_take_up = tax_unit("simulated_aca_take_up_if_eligible", period)
        return reported_marketplace_coverage | simulated_take_up
