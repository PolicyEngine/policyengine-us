from policyengine_us.model_api import *


class az_family_tax_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Family Tax Credit Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.family_tax_credits
        income = tax_unit("az_agi", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        dependents = tax_unit("tax_unit_dependents", period)
        max_income = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                p.income_limit.single,
                p.income_limit.joint.calc(dependents),
                p.income_limit.head_of_household.calc(dependents),
                p.income_limit.separate,
                p.income_limit.widow.calc(dependents),
            ],
        )
        return income <= max_income
