from policyengine_us.model_api import *


class is_cdcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CDCC-eligible"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#b_1",
        "https://www.law.cornell.edu/uscode/text/26/21#e_5",
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
        qualifies_by_age = ~head_or_spouse & (age < p.child_age)
        # Subsections (b)(1)(B) (dependent) and (b)(1)(C) (spouse).
        disabled = person("is_incapable_of_self_care", period)
        married = person.tax_unit("tax_unit_married", period)
        qualifies_by_disability = disabled & (is_dependent | (head_or_spouse & married))
        return qualifies_by_age | qualifies_by_disability
