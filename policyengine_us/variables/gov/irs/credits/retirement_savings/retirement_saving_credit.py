from policyengine_us.model_api import *


class savers_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Retirement Savings Credit"
    unit = USD
    reference = "https://www.irs.gov/pub/irs-pdf/f8880.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        person = tax_unit.members
        person_eligible = person("retirement_saving_eligible_person", period)
        agi_person = (
            person("adjusted_gross_income_person", period) * person_eligible
        )
        total_agi = tax_unit.sum(agi_person)
        qualified_contributions = add(
            person,
            period,
            [
                "traditional_ira_contributions",
                "roth_ira_contributions",
                "roth_401k_contributions",
                "traditional_401k_contributions",
            ],
        )
        capped_qualified_contributions = min_(
            qualified_contributions, p.contributions_cap
        )
        total_capped_qualified_contributions = tax_unit.sum(
            capped_qualified_contributions
        )
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values

        credit_rate = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rate.single.calc(total_agi),
                p.rate.separate.calc(total_agi),
                p.rate.joint.calc(total_agi),
                p.rate.widow.calc(total_agi),
                p.rate.head_of_household.calc(total_agi),
            ],
        )
        return credit_rate * total_capped_qualified_contributions
