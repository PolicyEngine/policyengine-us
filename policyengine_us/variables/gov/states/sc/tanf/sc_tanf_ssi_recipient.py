from policyengine_us.model_api import *


class sc_tanf_ssi_recipient(Variable):
    value_type = bool
    entity = Person
    label = "South Carolina TANF SSI recipient"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=117"  # Section 7.7, SSI benefit

    def formula(person, period, parameters):
        # Section 7.7 excludes the SSI recipient and his or her income when
        # determining benefits for the other benefit group members. Reported
        # receipt also counts, covering people the model computes as $0.
        return (person("ssi", period) > 0) | person("receives_ssi", period)
