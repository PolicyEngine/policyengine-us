from policyengine_us.model_api import *


class ca_sbd_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Bernardino County General Relief"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
        "https://wp.sbcounty.gov/tad/wp-content/uploads/sites/25/2025/06/gr000101-4.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.sbd.general_relief
        # The flat maximum-basic-grant design took effect June 1, 2021; the
        # prior needs-based design is not modeled.
        if not p.in_effect:
            return False
        person = spm_unit.members
        eligible_person = person("ca_sbd_general_relief_eligible_person", period)
        # General Relief serves needy adults; children participate only
        # through a parent applicant. County materials state no age, so the
        # model-wide adult definition (18 or older, matching California
        # Family Code section 6501) supplies the threshold.
        adult = person("is_adult", period.this_year)
        has_eligible_adult = spm_unit.any(eligible_person & adult)
        income_eligible = spm_unit("ca_sbd_general_relief_income_eligible", period)
        resources_eligible = spm_unit(
            "ca_sbd_general_relief_resources_eligible", period
        )
        return has_eligible_adult & income_eligible & resources_eligible
