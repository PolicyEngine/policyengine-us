from policyengine_us.model_api import *

class mt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MT CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Montana Child Tax Credit"
    reference = "https://leg.mt.gov/bills/2023/billpdf/HB0268.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # int amount of credit for each qualifying child
        # int number of qualifying children
        # bool proof of earned income & valid SSN for each child
        # float investment income (has to be less than 10_300)
        # float earned income/tax liability (tax credit can't exceed tax liability)
        # int age of each child

        p = parameters(period).gov.states.mt.tax.income.credits.ctc
        # income limit
        income_eligible = (
            tax_unit("adjusted_gross_income", period) <= p.income_threshold
        )
        investment_income_eligible = (
            tax_unit("investment_income", period) <= p.investment_threshold
        )
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        meets_age_limit = person("age", period) < p.child_age_eligibility
        eligible_child = dependent & meets_age_limit
        eligible_children = tax_unit.sum(eligible_child)
        # implent reduction
        return income_eligible * investment_income_eligible * eligible_children * p.amount