from policyengine_us.model_api import *


class takes_up_nm_puente_health_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit takes up New Mexico Puente Health"
    definition_period = YEAR
    defined_for = StateCode.NM
    documentation = (
        "Puente Health pays only for plans bought on BeWell, so by default an "
        "eligible tax unit takes it up when it takes up Marketplace coverage "
        "(takes_up_aca_if_eligible). Take-up is assigned during microdata "
        "construction; a supplied value overrides this default."
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("takes_up_aca_if_eligible", period)
