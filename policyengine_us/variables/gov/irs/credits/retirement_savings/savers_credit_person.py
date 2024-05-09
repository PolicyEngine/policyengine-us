from policyengine_us.model_api import *


class savers_credit_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Retirement Savings Credit for eahc individual person"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
        "https://www.law.cornell.edu/uscode/text/26/25B#d_2",
    )
    defined_for = "savers_credit_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving

        qualified_contributions = person(
            "savers_qualified_contributions", period
        )
        capped_qualified_contributions = min_(
            qualified_contributions, p.contributions_cap
        )

        agi = person.tax_unit("adjusted_gross_income", period)

        # AGI threshold for the rate
        filing_status = person.tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        # Joint as the base

        threshold_adjustment = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rate.threshold_adjustment.single,
                p.rate.threshold_adjustment.separate,
                p.rate.threshold_adjustment.widow,
                p.rate.threshold_adjustment.head_of_household,
            ],
            default=1,
        )
        # Credit rate
        adjusted_agi = agi / threshold_adjustment
        credit_rate = p.rate.joint.calc(adjusted_agi)
        return credit_rate * capped_qualified_contributions
