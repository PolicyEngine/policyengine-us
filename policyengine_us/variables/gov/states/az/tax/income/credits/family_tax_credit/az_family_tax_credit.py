from policyengine_us.model_api import *


class az_family_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Family Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period) 
        status = filing_status.possible_values
        dependents = tax_unit("tax_unit_dependents", period)
        head = tax_unit.any(person("is_tax_unit_head", period).astype(int))
        spouse = tax_unit.any(person("is_tax_unit_spouse", period).astype(int))
        max_income = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                p.eligibility.single,
                p.eligibility.joint.calc(dependents),
                p.eligibility.head_of_household.calc(dependents),
                p.eligibility.separate,
                p.eligibility.widow.calc(dependents),
                ]

        )
        household_size = (head + spouse + dependents)
        amount = p.amount * household_size
        eligible = income <= max_income
        return eligible * min_(amount, p.max_amount[filing_status])  
