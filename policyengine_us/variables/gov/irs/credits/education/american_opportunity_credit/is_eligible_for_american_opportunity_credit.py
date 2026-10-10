from policyengine_us.model_api import *


class is_eligible_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for American Opportunity Credit"
    documentation = "Whether the person is eligible for the AOC in respect of qualified tuition expenses for this tax year. The expenses must be for one of the first four years of post-secondary education, and the person must not have claimed the AOC for any four previous tax years."
    definition_period = YEAR
    reference = [
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A",
        "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title20-section1091",
    ]

    def formula(person, period, parameters):
        aoc = parameters(period).gov.irs.credits.education.american_opportunity_credit
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        filing_status_values = filing_status.possible_values
        filing_status_eligible = filing_status != filing_status_values.SEPARATE
        # IRC 25A(g)(3): no credit to an individual for whom a section 151
        # deduction "is allowed to another taxpayer", and the Form 1040
        # instructions extend this to "your spouse if filing jointly", so
        # either filer being claimed bars the return's credit. This turns on
        # an actual claim (26 CFR 1.25A-1(f)), so it reads the claimed input
        # rather than a claimability helper.
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        filer_claimed = tax_unit.any(filer & claimed)
        requires_1098_t = aoc.eligibility.requires_1098_t_or_exception
        has_1098_t_or_exception = (
            person("has_american_opportunity_credit_1098_t_or_exception", period)
            if requires_1098_t
            else True
        )
        requires_institution_ein = aoc.eligibility.requires_institution_ein
        has_institution_ein = (
            person("has_american_opportunity_credit_institution_ein", period)
            if requires_institution_ein
            else True
        )

        return (
            person("is_pursuing_credential_for_american_opportunity_credit", period)
            & person(
                "attends_eligible_educational_institution_for_american_opportunity_credit",
                period,
            )
            & person(
                "is_enrolled_at_least_half_time_for_american_opportunity_credit",
                period,
            )
            & ~person(
                "has_completed_first_four_years_of_postsecondary_education",
                period,
            )
            & (person("american_opportunity_credit_claimed_prior_years", period) < 4)
            & ~person("has_felony_drug_conviction", period)
            & has_1098_t_or_exception
            & has_institution_ein
            & person(
                "meets_american_opportunity_credit_identification_requirements",
                period,
            )
            & tax_unit(
                "filer_meets_american_opportunity_credit_identification_requirements",
                period,
            )
            & ~tax_unit(
                "is_nonresident_alien_for_american_opportunity_credit",
                period,
            )
            & ~tax_unit(
                "is_barred_from_american_opportunity_credit_due_to_improper_claims",
                period,
            )
            & filing_status_eligible
            & ~filer_claimed
        )
