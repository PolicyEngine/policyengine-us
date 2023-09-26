from policyengine_us.model_api import *

class oh_joint_filing_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Joint Filing Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.05"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        credit = tax_unit("oh_income_tax_before_refundable_credits", period)
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.joint_filing_credit
        income = person("employment_income", period) 
        print(income)
        #income_condition = income >= p.income_base
        head_income = tax_unit.sum(is_head*income)
       
        spouse_income = tax_unit.sum(is_spouse*income)
       
        qualify_income = (head_income>=p.income_base) & (spouse_income>=p.income_base)
        print(qualify_income)
        qualify_status = filing_status == filing_status.possible_values.JOINT
        magi_less_exepmtion = tax_unit("oh_agi", period) - tax_unit("oh_income_tax_exempt", period)
        percentage = where(qualify_income & qualify_status, p.rate.calc(magi_less_exepmtion), 0)
        return min_(credit*percentage, p.max_amount)

