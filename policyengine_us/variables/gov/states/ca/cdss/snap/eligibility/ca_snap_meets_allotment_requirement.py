from policyengine_us.model_api import *


class ca_snap_meets_allotment_requirement(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = True
    defined_for = StateCode.CA
    label = "Meets California SNAP allotment requirement"
    documentation = (
        "California denies or discontinues CE/MCE households of three or more "
        "with zero calculated allotments. One- and two-person households retain "
        "their minimum allotment. Applies from the model's October 2015 MCE "
        "baseline; initial-month proration and issuance exceptions are not modeled."
    )
    reference = (
        "https://www.cdss.ca.gov/lettersnotices/entres/getinfo/acl/2014/14-56.pdf#page=6",
        "https://www.cdss.ca.gov/lettersnotices/entres/getinfo/acl/2014/14-63.pdf#page=2",
        "https://www.law.cornell.edu/cfr/text/7/273.10#e_2_iii",
    )

    def formula_2015_10_01(spm_unit, period, parameters):
        size = spm_unit("snap_unit_size", period)
        allotment = spm_unit("snap_allotment_before_eligibility", period)
        # This is a participation screen, not the regular net-income test.
        return (size < 3) | (allotment > 0)
