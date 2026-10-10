from policyengine_us.model_api import *


class is_medicaid_ltss_financial_threshold_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets modeled Medicaid LTSS financial thresholds"
    definition_period = MONTH
    documentation = (
        "is_medicaid_ltss_financial_threshold_eligible models selected state "
        "and waiver financial thresholds only. It does not determine actual "
        "Medicaid LTSS eligibility, service entitlement, or benefit amount."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.236",
        "https://www.law.cornell.edu/uscode/text/42/1396p",
        "https://www.law.cornell.edu/uscode/text/42/1396r-5",
    )

    def formula_2026_01_01(person, period, parameters):
        pathway = person("medicaid_ltss_financial_pathway", period)
        pathways = pathway.possible_values
        return (
            (pathway != pathways.UNMODELED)
            & person("is_medicaid_ltss_income_eligible", period)
            & person("medicaid_ltss_csra_resource_eligible", period)
            & person("medicaid_ltss_home_equity_eligible", period)
        )
