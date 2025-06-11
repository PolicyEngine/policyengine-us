from policyengine_us.model_api import *


class ny_2025_inflation_rebates(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York 2025 inflation rebates"
    unit = USD
    definition_period = YEAR
    reference = "https://www.governor.ny.gov/news/money-your-pockets-governor-hochul-proposes-sending-86-million-new-yorkers-inflation-refund"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.credits.ny_2025_inflation_rebates
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values

        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.surviving_spouse.calc(agi, right=True),
            ],
        )
