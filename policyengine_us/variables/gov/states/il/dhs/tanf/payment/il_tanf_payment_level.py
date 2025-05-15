from policyengine_us.model_api import *


class il_tanf_payment_level(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Illinois Temporary Assistance for Needy Families (TANF) payment level"
    )
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.payment_level
        fpg = spm_unit("il_tanf_assistance_unit_fpg", period)

        # The payment levels can vary by ssi eligibility:
        # If only the parent is receiving SSI, the payment level is 75%
        # if only the child is receiving SSI, the payment level is 25%
        parent_count = add(
            spm_unit, period, ["il_tanf_payment_eligible_parent"]
        )
        child_count = add(spm_unit, period, ["il_tanf_paymet_eligible_child"])

        parent_only = parent_count > 0 & child_count == 0
        child_only = child_count > 0 & parent_count == 0
        mix = parent_count > 0 & child_count > 0

        parent_only_payment = p.parent_only * p.rate * fpg
        child_only_payment = p.child_only * p.rate * fpg
        mix_payment = p.rate * fpg
        
        return select(
            [parent_only, child_only, mix],
            [parent_only_payment, child_only_payment, mix_payment],
            default=0,
        )
