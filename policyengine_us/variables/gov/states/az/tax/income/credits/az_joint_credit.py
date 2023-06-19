from policyengine_us.model_api import *


class az_joint_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "AZ joint credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period) 
        joint = filing_status == filing_status.possible_values.JOINT

        dependent = tax_unit("tax_unit_dependents", period)
        adult = tax_unit("num", period)


        phase_in_max_income = p.eligibility.joint.calc(dependent)
        eligible = income <= phase_in_max_income
        
        return min_(p.amount*(dependent + adult)*joint*eligible, 240)
