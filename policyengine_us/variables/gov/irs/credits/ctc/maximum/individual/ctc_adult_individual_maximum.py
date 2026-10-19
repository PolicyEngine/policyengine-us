from policyengine_us.model_api import *


class ctc_adult_individual_maximum(Variable):
    value_type = float
    entity = Person
    label = "CTC maximum amount (adult dependent)"
    unit = USD
    documentation = (
        "The CTC entitlement in respect of this person as an adult dependent."
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#a",
        "https://www.law.cornell.edu/uscode/text/26/24#h",
        "https://www.law.cornell.edu/uscode/text/26/24#i",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.ctc
        is_adult = person("ctc_child_individual_maximum", period) == 0
        dependent_has_tin = person("has_tin", period)
        filer_meets_tin_requirement = person.tax_unit(
            "filer_meets_ctc_identification_requirements", period
        )
        # IRC 24(h)(4)(A) gives the credit for "each dependent of the taxpayer";
        # under IRC 152(b)(1) a return on which the filer (or, if joint,
        # either spouse) can be claimed as a dependent has no dependents.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        return (
            is_adult
            * dependent_has_tin
            * filer_meets_tin_requirement
            * ~filer_is_dependent
            * p.amount.adult_dependent
        )
