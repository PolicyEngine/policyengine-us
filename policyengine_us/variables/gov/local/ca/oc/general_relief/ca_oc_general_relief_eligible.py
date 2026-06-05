from policyengine_us.model_api import *


class ca_oc_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Orange County General Relief"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/page/general-relief-regulations"

    def formula(spm_unit, period, parameters):
        # Categorical eligibility: at least one eligible person -- an adult who is
        # a qualified noncitizen and not receiving other cash assistance such as
        # SSI/SSP, CalWORKs, or CAPI (Sec 40, Sec 20.4).
        categorical_eligible = (
            spm_unit("ca_oc_general_relief_eligible_person_count", period) > 0
        )
        # Financial eligibility: net income below the maximum aid payment
        # (Sec 80.2.d) and resources within the limits (Sec 50, Sec 60).
        income_eligible = spm_unit(
            "ca_oc_general_relief_income_eligible",
            period,
        )
        resources_eligible = spm_unit(
            "ca_oc_general_relief_resources_eligible",
            period,
        )
        return categorical_eligible & income_eligible & resources_eligible
