from openfisca_us.model_api import *


class eitc_phaseout_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC phaseout start"
    unit = USD
    documentation = "Earnings above this level reduce EITC entitlement."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        num_children = tax_unit("eitc_child_count", period)
        eitc = parameters(period).irs.credits.eitc
        is_joint = tax_unit("tax_unit_is_joint", period)
        return (
            eitc.phaseout.start.calc(num_children)
            + is_joint * eitc.phaseout.joint_bonus
        )
