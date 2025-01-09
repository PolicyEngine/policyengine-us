from policyengine_us.model_api import *

class pr_compensatory_low_income_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for additional compensatory low income credit"
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age"

    def formula(person, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.low_income.additional
        # head or spouse check, 1
        head_or_spouse = person("is_tax_unit_head_or_spouse", period) 
        # check if pension below limit, 2  
        pension_lim = person("pension_income", period) <= p.income_limit 
        # is whole tax unit eligible, 3
        low_income_eligible = person.tax_unit("pr_low_income_credit_eligible", period) 
        return head_or_spouse & pension_lim & low_income_eligible

# Workflow:
# 1. Need to check if the person is a head or spouse 
# 2. Need to check if their pension income is below the parameter 
# Var: "pension_income" for income 
# 3. Check if the TaxUnit is elgible for the low income credit 
# to call a taxunit level variable: person.tax_unit()
# Return true if all conditions are met
