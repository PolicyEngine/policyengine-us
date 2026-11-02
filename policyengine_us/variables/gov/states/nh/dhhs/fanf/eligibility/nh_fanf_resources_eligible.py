from policyengine_us.model_api import *


class nh_fanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Hampshire FANF resources eligible"
    definition_period = YEAR
    reference = (
        "https://gc.nh.gov/rsa/html/xii/167/167-79.htm",
        "https://gc.nh.gov/rules/state_agencies/he-w600.html",
        "https://www.dhhs.nh.gov/fam_htm/html/403_resource_limits_fam.htm",
        "https://www.dhhs.nh.gov/sr_htm/html/sr_97-03_dated_02_97.htm",
        "https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/tanf-state-plan.pdf#page=25",
    )
    defined_for = StateCode.NH

    def formula(spm_unit, period, parameters):
        # NOTE: One vehicle per adult is excluded regardless of value.
        # Resource limits differ for applicants ($1,000) vs recipients ($5,000 as of 07/01/22)
        p = parameters(period).gov.states.nh.dhhs.fanf.resources
        resources = spm_unit("spm_unit_cash_assets", period)
        # He-W 656.06(a)(1) also treats an applicant who received FANF in any
        # one of the previous 6 months as a recipient. The inputs have no
        # 6-month look-back, so current enrollment stands in for it.
        is_enrolled = spm_unit("is_tanf_enrolled", period.first_month)
        limit = where(is_enrolled, p.recipient_limit, p.applicant_limit)
        # RSA 167:79 III(f): countable resources "shall be less than" the limit.
        return resources < limit
