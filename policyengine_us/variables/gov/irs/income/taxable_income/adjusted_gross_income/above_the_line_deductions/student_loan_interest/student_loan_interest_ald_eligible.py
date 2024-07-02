from policyengine_us.model_api import *


class student_loan_interest_ald_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Student loan interest ALD"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/221"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filing_status = person.tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        is_aoc_eligible = person(
            "is_eligible_for_american_opportunity_credit", period
        )
        return head_or_spouse & ~separate & is_aoc_eligible
