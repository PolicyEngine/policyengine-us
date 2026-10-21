from policyengine_us.model_api import *


class is_barred_from_education_credits_by_dependency(Variable):
    value_type = bool
    entity = Person
    label = "Barred from the education credits by the dependency rules"
    definition_period = YEAR
    reference = (
        # Subsections (f)(1)(A)(iii) and (g)(3).
        "https://www.law.cornell.edu/uscode/text/26/25A#g_3",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        "https://www.ecfr.gov/current/title-26/section-1.25A-1",
    )

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        # IRC 25A(g)(3): no credit to an individual for whom a section 151
        # deduction "is allowed to another taxpayer", and the Form 1040
        # instructions extend this to "your spouse if filing jointly", so
        # either filer being claimed bars the return's credit. This turns on
        # an actual claim (26 CFR 1.25A-1(f)), so it reads the claimed input
        # rather than a claimability helper.
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        filer_claimed = tax_unit.any(filer & claimed)
        # IRC 25A(f)(1)(A)(iii) counts the tuition of a dependent only if the
        # taxpayer "is allowed a deduction under section 151" for them, and a
        # return on which a filer can be claimed as a dependent (outside the
        # claimant filing exception) has no dependents (IRC 152(b)(1)).
        dependent_student_barred = person("is_tax_unit_dependent", period) & tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        return filer_claimed | dependent_student_barred
