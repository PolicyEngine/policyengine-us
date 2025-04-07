from policyengine_us.model_api import *


class ct_pension_annuity_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut pension and annuity subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        agi = tax_unit("adjusted_gross_income", period)
        
        p = parameters(period).gov.states.ct.tax.income.subtractions.pensions_or_annuity

        # Determine the appropriate rate parameter based on filing status
        rate_param = select(
            [
                filing_status == status.SINGLE or filing_status == status.SEPARATE or filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.JOINT or filing_status == status.SURVIVING_SPOUSE,
            ],
            [
                p.non_joint,
                p.joint,
            ]
        )
        
        # Get the rate based on AGI
        rate = rate_param.calc(agi)
        
        # Apply the rate to eligible pension income
        head_or_spouse = head | spouse
        pension_income = person("taxable_pension_income", period)
        eligible_pension = pension_income * head_or_spouse
        total_pension = tax_unit.sum(eligible_pension)
        
        return total_pension * rate
