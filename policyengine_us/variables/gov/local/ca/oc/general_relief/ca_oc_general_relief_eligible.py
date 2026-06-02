from policyengine_us.model_api import *


class ca_oc_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Orange County General Relief"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/page/general-relief-regulations"

    def formula(spm_unit, period, parameters):
        # Categorical screen: demographic (adults without minor children),
        # immigration, public-assistance, and resource rules. Financial
        # eligibility (income below the maximum aid payment) is applied in the
        # benefit variable ca_oc_general_relief, which nets countable income
        # against the MAP.
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
