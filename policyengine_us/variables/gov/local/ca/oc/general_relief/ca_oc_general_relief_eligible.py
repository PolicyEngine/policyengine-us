from policyengine_us.model_api import *


class ca_oc_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Partial eligibility screen for Orange County General Relief"
    documentation = (
        "Models available demographic, immigration, public assistance, and "
        "resource rules. It does not model the income limit, payment amount, "
        "or administrative eligibility rules because required Orange County "
        "schedules and history inputs are unavailable."
    )
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/page/general-relief-regulations"

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit(
            "ca_oc_general_relief_demographic_eligible",
            period,
        )
        resources_eligible = spm_unit(
            "ca_oc_general_relief_resources_eligible",
            period,
        )
        aided_person_count = spm_unit(
            "ca_oc_general_relief_aided_person_count",
            period,
        )
        return demographic_eligible & resources_eligible & (aided_person_count > 0)
