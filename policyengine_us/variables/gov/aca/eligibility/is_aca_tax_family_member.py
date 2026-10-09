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
    )
    documentation = (
        "Whether the person is in the taxpayer's family for the premium tax "
        "credit (Form 8962 line 1, tax family size). 26 CFR 1.36B-1(d)(2) "
        "defines the family as the taxpayer, both spouses on a joint return, "
        "'except for individuals who qualify as a dependent of another "
        "taxpayer', plus the dependents the taxpayer claims. A head or spouse "
        "who can be claimed on another return is therefore not a member "
        "(IRC 36B(c)(1)(D), 26 CFR 1.36B-2(b)(3)), and on a joint return the "
        "other spouse still is. A return with a filer who can be claimed "
        "elsewhere claims no dependents (IRC 152(b)(1)), so its dependents "
        "are members only when no head or spouse can be claimed elsewhere. "
        "The claimed flag of a dependent on this return does not matter: this "
        "return claims them."
    )

    def formula(person, period, parameters):
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed_elsewhere = person("claimed_as_dependent_on_another_return", period)
        return_has_claimed_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return where(filer, ~claimed_elsewhere, ~return_has_claimed_filer)
