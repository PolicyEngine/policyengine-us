from policyengine_us.model_api import *


class tx_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2420-eligibility-requirements",
        "https://www.law.cornell.edu/regulations/texas/title-1/part-15/chapter-372/subchapter-B",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        non_financial_eligible = spm_unit(
            "tx_tanf_non_financial_eligible", period
        )
        income_eligible = spm_unit("tx_tanf_income_eligible", period)
        resources_eligible = spm_unit("tx_tanf_resources_eligible", period)
        meets_work_requirements = spm_unit(
            "tx_tanf_meets_work_requirements", period
        )

        return (
            non_financial_eligible
            & income_eligible
            & resources_eligible
            & meets_work_requirements
        )
