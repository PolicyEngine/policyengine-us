from policyengine_us.model_api import *


class savers_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Retirement Savings Credit"
    unit = USD
    reference = ("https://www.irs.gov/pub/irs-pdf/f8880.pdf" , "https://www.law.cornell.edu/uscode/text/26/25B#c")
    defined_for = "savers_credit_agi_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        person = tax_unit.members
        eligible_person = person("savers_credit_eligible_person", period)
        agi = person("adjusted_gross_income_person", period) * eligible_person
        total_agi = tax_unit.sum(agi)

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

        # AGI threshold for the rate
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        # Joint as the base
        agi_threshold_joint = p.rate.joint.threshold
        # Match others filing status based on the joint
        match = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rate.match.single,
                p.rate.match.separate,
                p.rate.match.widow,
                p.rate.match.head_of_household,
            ],
            default=1,
        )
        # Credit rate
        joint_credit_rate = select(
            [
                total_agi < agi_threshold_joint.lower * match,
                total_agi < agi_threshold_joint.middle * match,
                total_agi < agi_threshold_joint.higher * match,
            ],
            [
                p.rate.joint.rate.lower,
                p.rate.joint.rate.middle,
                p.rate.joint.rate.higher,
            ],
            default=0,
        )

        return joint_credit_rate * total_capped_qualified_contributions
