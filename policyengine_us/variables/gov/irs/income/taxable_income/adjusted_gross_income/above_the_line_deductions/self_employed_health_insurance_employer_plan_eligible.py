from policyengine_us.model_api import *


class self_employed_health_insurance_employer_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for a subsidized employer health plan (self-employed health insurance deduction)"
    documentation = (
        "Whether the person, or their spouse, is eligible for a subsidized "
        "health plan of their employer, which bars the self-employed health "
        "insurance deduction for the premiums (26 U.S.C. 162(l)(2)(B); Form "
        "7206 line 1). The law applies the bar month by month; the inputs are "
        "annual, so a person eligible at any point is treated as eligible for "
        "the whole year. Two cases are not modeled. A spouse who files "
        "separately is in another tax unit, and the model does not see their "
        "employer's plan; it cannot use the filing status here, which depends "
        "on dependents' incomes and so on this deduction, and the default "
        "dataset has no married couple split across tax units. The plan of a "
        "dependent's or under-27 child's employer bars the deduction only for "
        "a taxpayer who can take part in it, and no input records that."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_B",
        "https://www.irs.gov/pub/irs-prior/f7206--2025.pdf#page=1",  # Line 1, first bullet
        "https://www.irs.gov/pub/irs-prior/i7206--2025.pdf#page=2",  # Other coverage
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=88",  # Line 17, before Form 7206
    )

    def formula(person, period, parameters):
        # Enrolled in, or offered, employer coverage, or the employer pays some
        # or all of the premiums. Enrollment and an offer each show the person
        # can take part in the plan. An employer that pays premiums subsidizes
        # the plan.
        contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        contribution_status = contribution.possible_values
        employer_pays = (contribution == contribution_status.SOME) | (
            contribution == contribution_status.ALL
        )
        own = (
            person("has_esi", period)
            | person("offered_aca_disqualifying_esi", period)
            | employer_pays
        )
        # The plan of the spouse's employer also bars the deduction: on a joint
        # return, the other of the head and spouse. A tax unit dependent's own
        # deduction is not barred by the plan of a parent's employer, which
        # the statute does not list.
        filer = person("is_tax_unit_head_or_spouse", period)
        filer_own = own & filer
        other_filer_eligible = person.tax_unit.sum(filer_own) > filer_own.astype(int)
        return own | (filer & other_filer_eligible)
