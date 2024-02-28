from policyengine_us.model_api import *


class retirement_saving_credit(Variable):
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
        ira_contributions = add(
            person,
            period,
            ["traditional_ira_contributions", "roth_ira_contributions"],
        )
        capped_ira_contributions = min_(ira_contributions, p.cap)
        qualified_ira = tax_unit.sum(capped_ira_contributions)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values

        return select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.WIDOW,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rate.single.calc(total_agi) * qualified_ira,
                p.rate.separate.calc(total_agi) * qualified_ira,
                p.rate.joint.calc(total_agi) * qualified_ira,
                p.rate.widow.calc(total_agi) * qualified_ira,
                p.rate.head_of_household.calc(total_agi) * qualified_ira,
            ],
        )
