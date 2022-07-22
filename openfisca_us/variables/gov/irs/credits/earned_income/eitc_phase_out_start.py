from openfisca_us.model_api import *


class eitc_phase_out_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phase-out start"
    unit = USD
    documentation = "Earnings above this level reduce EITC entitlement."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        count_children = tax_unit("eitc_child_count", period)
        eitc = parameters(period).gov.irs.credits.eitc
        is_joint = tax_unit("tax_unit_is_joint", period)
        joint_bonus = eitc.phase_out.joint_bonus.calc(count_children)
        phase_out_start = eitc.phase_out.start.calc(count_children)
        return phase_out_start + is_joint * joint_bonus
