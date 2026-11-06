from policyengine_us.model_api import *


class self_employed_health_insurance_employer_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for a subsidized employer health plan (self-employed health insurance deduction)"
    documentation = (
        "Employer-plan eligibility that bars the self-employed health insurance "
        "deduction under 26 U.S.C. 162(l)(2)(B) and Form 7206 line 1. For the "
        "head and spouse, the model reads has_esi, offered_aca_disqualifying_esi, "
        "or employer contributions of SOME or ALL as access to a subsidized "
        "plan of the person's own or spouse's employer. Either joint filer's "
        "flags bar both filers. For tax unit dependents, only their own employer "
        "contributions of SOME or ALL count. Their enrollment and offer flags "
        "can describe a parent's employer plan: 26 CFR 1.36B-2(c)(3)(i)(A) "
        "includes related individuals, while section 162(l)(2)(B) does not "
        "list a parent's employer for the dependent's deduction. The inputs "
        "identify neither the employer that maintains a plan nor its subsidy. "
        "The model cannot distinguish an unsubsidized plan, a spouse's plan "
        "the taxpayer cannot join, or a parent's plan for a nondependent filer, "
        "such as a 25-year-old. An unaffordable subsidized offer can bar the "
        "deduction even though offered_aca_disqualifying_esi leaves it out. "
        "A QSEHRA counts only if entered through the contribution input. The "
        "law applies the bar month by month; the model applies annual "
        "eligibility to the whole year. It does not model a spouse who files "
        "separately in another tax unit, or the taxpayer's access to a "
        "dependent's or under-27 child's employer plan. Filing status depends "
        "on dependents' incomes and this deduction, so reading it here would "
        "create a cycle."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_B",
        "https://www.irs.gov/pub/irs-prior/f7206--2025.pdf#page=1",  # Line 1, first bullet
        "https://www.irs.gov/pub/irs-prior/i7206--2025.pdf#page=2",  # Other coverage
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=88",  # Line 17, before Form 7206
        "https://www.ecfr.gov/current/title-26/section-1.36B-2#p-1.36B-2(c)(3)(i)(A)",
    )

    def formula(person, period, parameters):
        contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        contribution_status = contribution.possible_values
        employer_pays = (contribution == contribution_status.SOME) | (
            contribution == contribution_status.ALL
        )
        filer = person("is_tax_unit_head_or_spouse", period)
        # Read filers' enrollment and offer flags as access through their own
        # or spouse's employer. A dependent's flags can describe a parent's
        # plan, so require their own employer's contribution instead.
        own = employer_pays | (
            filer
            & (
                person("has_esi", period)
                | person("offered_aca_disqualifying_esi", period)
            )
        )
        # Either joint filer's eligibility bars both filers. A dependent's
        # employer contribution does not establish a parent's access.
        filer_own = own & filer
        return own | (filer & person.tax_unit.any(filer_own))
