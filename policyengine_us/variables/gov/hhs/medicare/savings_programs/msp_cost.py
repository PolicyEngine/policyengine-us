from policyengine_us.model_api import *


class msp_cost(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program cost"
    definition_period = YEAR
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_E",
        "https://www.law.cornell.edu/uscode/text/42/1396d#p_3",
    )
    documentation = (
        "Annual limited-benefit Medicare Savings Program cost for MSP-only "
        "beneficiaries. This is zero for full Medicaid enrollees to avoid "
        "double counting the same person as both a limited-benefit MSP "
        "beneficiary and a full-benefit Medicaid enrollee."
    )

    def formula(person, period, parameters):
        monthly_cost = 0
        for month in period.get_subperiods(MONTH):
            monthly_cost += person("msp_benefit_value", month) + person(
                "qmb_cost_sharing", month
            )
        return where(person("medicaid_enrolled", period), 0, monthly_cost)
