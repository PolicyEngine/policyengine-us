from policyengine_us.model_api import *


class sc_tanf_benefit_group_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "South Carolina TANF benefit group size"
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 56, 117
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=56"  # Sections 3.6 and 7.7

    def formula(spm_unit, period, parameters):
        # Section 3.6 excludes an SSI recipient living with the benefit group;
        # if an SSI child is the only child, the parents are the only members.
        ssi_recipient = spm_unit.members("sc_tanf_ssi_recipient", period)
        return spm_unit.sum(~ssi_recipient)
