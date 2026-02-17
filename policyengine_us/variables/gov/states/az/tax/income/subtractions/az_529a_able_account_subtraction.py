from policyengine_us.model_api import *


class az_529a_able_account_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona 529A ABLE account subtraction"
    unit = USD
    documentation = "https://www.azleg.gov/ars/43/01022.htm"
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.subtractions.able_account

        filing_status = tax_unit("az_filing_status", period)
        contributions = tax_unit("able_contributions", period)

        cap = p.cap[filing_status]

        return min_(contributions, cap)
