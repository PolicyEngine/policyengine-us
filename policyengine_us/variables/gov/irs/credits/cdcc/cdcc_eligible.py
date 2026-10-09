from policyengine_us.model_api import *


class is_cdcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CDCC-eligible"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#b_1",
        "https://www.law.cornell.edu/uscode/text/26/21#e_5",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        # Publication 503, Who Is a Qualifying Person?
        "https://www.irs.gov/pub/irs-prior/p503--2025.pdf#page=3",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.irs.credits.cdcc.eligibility
        # Subsection (b)(1)(A): a dependent under age 13. Under 21(e)(5), a
        # child of divorced or separated parents is the custodial parent's
        # qualifying individual even when the noncustodial parent claims the
        # dependent, so any under-age member other than the head or spouse
        # qualifies.
        # A child qualifies only as the filer's dependent ("Your qualifying
        # child who is your dependent", Publication 503), and under IRC
        # 152(b)(1) a return on which the filer (or, if joint, either spouse)
        # can be claimed as a dependent has no dependents.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        qualifies_by_age = ~head_or_spouse & (age < p.child_age) & ~filer_is_dependent
        # Subsections (b)(1)(B) (dependent) and (b)(1)(C) (spouse). Subsection
        # (b)(1)(B) determines dependency "without regard to subsections
        # (b)(1), (b)(2), and (d)(1)(B)" of section 152, so a disabled person
        # still qualifies when the filer can be claimed as a dependent.
        disabled = person("is_incapable_of_self_care", period)
        married = person.tax_unit("tax_unit_married", period)
        qualifies_by_disability = disabled & (is_dependent | (head_or_spouse & married))
        return qualifies_by_age | qualifies_by_disability
