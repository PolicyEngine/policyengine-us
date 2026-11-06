from policyengine_us.model_api import *


class self_employed_health_insurance_employer_plan_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for a subsidized employer health plan (self-employed health insurance deduction)"
    documentation = (
        "The model identifies people whose employer-plan eligibility bars "
        "their Form 7206 line 1 deduction under 26 U.S.C. 162(l)(2)(B). For "
        "the head and spouse, the model counts has_esi, "
        "offered_aca_disqualifying_esi, or employer contributions of SOME or "
        "ALL as access through their own or their spouse's employer. The "
        "model bars both joint filers if either meets that test. For tax unit "
        "dependents, the model counts only their own employer contributions "
        "of SOME or ALL. It ignores their enrollment and offer flags because "
        "those inputs can describe a parent's plan. Treasury includes related "
        "individuals in employer offers under 26 CFR 1.36B-2(c)(3)(i)(A); "
        "Congress does not list a parent's employer for the dependent's "
        "deduction. The model assumes a subsidy when a filer has ESI or an "
        "ACA-disqualifying offer, and assumes that each joint filer can join "
        "the other's plan. The inputs identify neither the employer "
        "maintaining a plan nor its subsidy or family eligibility. The model "
        "cannot distinguish an unsubsidized plan, a spouse's plan the "
        "taxpayer cannot join, or a parent's plan for a nondependent filer, "
        "such as a 25-year-old. It misses unaffordable subsidized offers "
        "because offered_aca_disqualifying_esi covers only affordable, "
        "minimum-value offers. No input records a QSEHRA; the model counts "
        "one only through the contribution category. Congress bars premiums "
        "month by month; the model applies annual eligibility to the whole "
        "year. The model cannot see a separately filing spouse in another tax "
        "unit or establish the taxpayer's access to a dependent's or under-27 "
        "child's employer plan. The model would create a cycle if it read "
        "filing status here, because that status depends on dependents' "
        "incomes and this deduction. Congress applies separate eligibility "
        "tests to medical and long-term care plans under section "
        "162(l)(2)(B)(i)-(ii). The model bars only line 1 premiums because no "
        "input records employer long-term care plan eligibility; eligible "
        "long-term care premiums still enter the deduction on line 2."
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
