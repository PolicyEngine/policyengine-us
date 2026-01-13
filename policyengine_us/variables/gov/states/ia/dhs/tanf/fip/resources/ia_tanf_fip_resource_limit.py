from policyengine_us.model_api import *


class ia_tanf_fip_resource_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP resource limit"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.26"
    documentation = (
        "The applicable resource limit is $2,000 for applicants or "
        "$5,000 for recipients who received FIP in the prior month."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.tanf.fip.resources

        # Check if family received FIP in prior month
        prior_month = period.last_month
        received_fip_prior_month = spm_unit("ia_tanf_fip", prior_month)

        # Use recipient limit if received FIP last month, otherwise applicant limit
        return where(
            received_fip_prior_month > 0,
            p.limit_recipient,
            p.limit_applicant,
        )
