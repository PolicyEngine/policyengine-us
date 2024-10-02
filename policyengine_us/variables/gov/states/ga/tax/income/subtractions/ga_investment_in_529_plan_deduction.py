from policyengine_us.model_api import *


class ga_investment_in_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia investment in 529 plan deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet"
        "https://casetext.com/regulation/georgia-administrative-code/department-560-rules-of-department-of-revenue/chapter-560-7-income-tax-division/subject-560-7-4-net-taxable-income-individual/rule-560-7-4-04-procedures-governing-the-georgia-higher-education-savings-plan"
    )
    defined_for = StateCode.GA
