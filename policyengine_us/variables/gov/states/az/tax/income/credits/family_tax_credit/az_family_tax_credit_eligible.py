from policyengine_us.model_api import *


class az_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Family Tax Credit"
    definition_period = YEAR
    reference = "https://www.azleg.gov/ars/43/01073.htm"
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.family_tax_credits
        # Per ARS 43-1073: "Arizona adjusted gross income, plus the amount
        # subtracted for exemptions under section 43-1023"
        az_agi = tax_unit("az_agi", period)
        exemptions = tax_unit("az_exemptions", period)
        income = az_agi + exemptions
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
