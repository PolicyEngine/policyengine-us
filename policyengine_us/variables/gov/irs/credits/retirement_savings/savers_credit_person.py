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
            "savers_credit_qualified_contributions", period
        )
        capped_qualified_contributions = min_(
            qualified_contributions, p.contributions_cap
        )

        agi = person.tax_unit("adjusted_gross_income", period)

        # AGI threshold for the rate
        filing_status = person.tax_unit("filing_status", period)
        # Joint as the base
        threshold_adjustment = p.rate.threshold_adjustment[filing_status]
        # Credit rate
        adjusted_agi = agi / threshold_adjustment
        credit_rate = p.rate.joint.calc(adjusted_agi)
        return credit_rate * capped_qualified_contributions
