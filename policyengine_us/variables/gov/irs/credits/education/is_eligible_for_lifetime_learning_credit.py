from policyengine_us.model_api import *


class is_eligible_for_lifetime_learning_credit(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Lifetime Learning Credit"
    documentation = "Whether the person is eligible for the Lifetime Learning Credit in respect of qualified tuition expenses for this tax year."
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/25A#c",
        "https://www.law.cornell.edu/uscode/text/26/25A#f",
        "https://www.law.cornell.edu/uscode/text/26/25A#g",
    ]

    def formula(person, period, parameters):
        llc = parameters(period).gov.irs.credits.education.lifetime_learning_credit
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        filing_status_values = filing_status.possible_values
        filing_status_eligible = filing_status != filing_status_values.SEPARATE
        requires_1098_t = llc.eligibility.requires_1098_t_or_exception
        has_1098_t_or_exception = (
            person("has_lifetime_learning_credit_1098_t_or_exception", period)
            if requires_1098_t
            else True
        )

        return (
            person(
                "attends_eligible_educational_institution_for_lifetime_learning_credit",
                period,
            )
            & has_1098_t_or_exception
            & person(
                "meets_lifetime_learning_credit_identification_requirements",
                period,
            )
            & tax_unit(
                "filer_meets_lifetime_learning_credit_identification_requirements",
                period,
            )
            & ~tax_unit(
                "is_nonresident_alien_for_lifetime_learning_credit",
                period,
            )
            & filing_status_eligible
        )
