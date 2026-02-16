from policyengine_us.model_api import *


class mt_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Montana Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.206",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.228",
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        # demographic_eligible checks for any eligible child/pregnant person;
        # has_assistance_unit_members checks AU size > 0, since a child can be
        # demographic-eligible but excluded from the AU by SSI or foster care.
        demographic_eligible = (
            add(spm_unit, period, ["mt_tanf_demographic_eligible_person"]) > 0
        )
        has_assistance_unit_members = (
            spm_unit("mt_tanf_assistance_unit_size", period) > 0
        )
        income_eligible = spm_unit("mt_tanf_income_eligible", period)
        resources_eligible = spm_unit("mt_tanf_resources_eligible", period)

        meets_work_requirements = spm_unit(
            "mt_tanf_meets_work_requirements", period
        )
        return (
            demographic_eligible
            & has_assistance_unit_members
            & meets_work_requirements
            & income_eligible
            & resources_eligible
        )
