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
    )
    defined_for = "savers_credit_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving

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
        credit_rate = select(
            [
                agi < p.rate.joint.thresholds[1] * threshold_adjustment,
                agi < p.rate.joint.thresholds[2] * threshold_adjustment,
                agi < p.rate.joint.thresholds[3] * threshold_adjustment,
            ],
            [
                p.rate.joint.amounts[0],
                p.rate.joint.amounts[1],
                p.rate.joint.amounts[2],
            ],
            default=0,
        )
        return credit_rate * capped_qualified_contributions
