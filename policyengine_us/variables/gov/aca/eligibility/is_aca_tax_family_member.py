from policyengine_us.model_api import *


class is_aca_tax_family_member(Variable):
    value_type = bool
    entity = Person
    label = "Member of the premium tax credit tax family"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1_D",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-1#d_2",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-2#b_3",
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )
    documentation = (
        "Whether the person is in an applicable taxpayer's family for the "
        "premium tax credit (Form 8962 line 1, tax family size). 26 CFR "
        "1.36B-1(d)(2) defines the family as the taxpayer, both spouses on a "
        "joint return, 'except for individuals who qualify as a dependent of "
        "another taxpayer', plus the dependents the taxpayer claims. A head or "
        "spouse who can be claimed on another return "
        "(claimable_as_dependent_on_another_return, whether or not claimed) "
        "is not a member; on a joint return the other spouse still is. Such a "
        "return claims no dependents (IRC 152(b)(1)) unless the would-be "
        "claimant meets the refund-only filing exception (Publication 501, "
        "Dependent Taxpayer Test). No credit is allowed to someone another "
        "taxpayer can claim (IRC 36B(c)(1)(D)), so a return whose every head "
        "and spouse can be claimed has no applicable taxpayer and no family "
        "for the credit. A tax unit with neither a head nor a spouse (role "
        "inference makes the oldest adult the head, so a unit of minors has "
        "none) is treated as filed by its oldest member: everyone is in the "
        "family if that member cannot be claimed elsewhere, and nobody is if "
        "they can. A "
        "dependent on a return with an applicable taxpayer is a member even if "
        "another taxpayer could also claim them: this return claims them."
    )

    def formula(person, period, parameters):
        filer = person("is_tax_unit_head_or_spouse", period)
        claimable = person("claimable_as_dependent_on_another_return", period)
        has_filer = person.tax_unit.any(filer)
        applicable_taxpayer = (
            person.tax_unit("head_spouse_count_not_dependent_elsewhere", period) > 0
        )
        claims_dependents = ~person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependent_member = applicable_taxpayer & claims_dependents
        # No head or spouse: the oldest member files.
        age = person("age", period)
        oldest = person.get_rank(person.tax_unit, -age) == 0
        oldest_claimable = person.tax_unit.any(oldest & claimable)
        return where(
            has_filer,
            where(filer, ~claimable, dependent_member),
            ~oldest_claimable,
        )
