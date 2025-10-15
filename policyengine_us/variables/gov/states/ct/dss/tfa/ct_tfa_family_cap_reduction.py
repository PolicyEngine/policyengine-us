"""
Connecticut TFA family cap benefit reduction.
"""

from policyengine_us.model_api import *


class ct_tfa_family_cap_reduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA family cap reduction amount"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "The amount by which the Connecticut TFA benefit is reduced due to the "
        "partial family cap policy. When the family cap applies, the benefit "
        "increase for additional children born within 10 months of application "
        "is reduced by 50%."
    )
    reference = (
        "Connecticut General Assembly OLR Report 98-R-0058; "
        "SSA POMS SI BOS00830.403 - TANF - Connecticut, Family Cap Policy; "
        "https://www.cga.ct.gov/PS98/rpt/olr/htm/98-R-0058.htm"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.family_cap

        family_cap_applies = spm_unit("ct_tfa_family_cap_applies", period)

        # If family cap applies, calculate the reduction
        # NOTE: This would require calculating the benefit increase for the new child
        # and then applying the 50% reduction. Since family_cap_applies is currently
        # always False (due to data limitations), this will return 0.
        # A full implementation would calculate:
        # 1. Payment standard for (current_size)
        # 2. Payment standard for (current_size - 1)
        # 3. Increment = difference
        # 4. Reduction = increment * reduction_percentage

        reduction_percentage = p.reduction_percentage

        # Placeholder: return 0 when family cap doesn't apply
        return where(family_cap_applies, 0, 0)
