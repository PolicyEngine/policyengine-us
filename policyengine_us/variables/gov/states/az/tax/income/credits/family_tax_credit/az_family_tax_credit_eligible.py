from policyengine_us.model_api import *


class az_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Family Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.family_tax_credits
        income = tax_unit("az_agi", period)
        filing_status = tax_unit("az_filing_status", period)
        status = filing_status.possible_values
        dependents = tax_unit("tax_unit_dependents", period)
        income_limit = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
            ],
            [
                p.income_limit.single,
                p.income_limit.joint.calc(dependents),
                p.income_limit.head_of_household.calc(dependents),
                p.income_limit.separate,
            ],
        )
        return income <= income_limit
