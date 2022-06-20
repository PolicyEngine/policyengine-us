from openfisca_us.model_api import *


class eitc_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phase-out start"
    unit = USD
    documentation = "Earnings above this level reduce EITC entitlement."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        num_children = tax_unit("eitc_child_count", period)
        eitc = parameters(period).gov.irs.credits.eitc
        is_joint = tax_unit("tax_unit_is_joint", period)
        return (
            eitc.phase_out.start.calc(num_children)
            + is_joint * eitc.phase_out.joint_bonus
        )
