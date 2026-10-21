from policyengine_us.model_api import *


class rrc_adult_count_with_valid_ssn(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Count of tax unit head/spouse with valid SSN for RRC"
    reference = (
        # Subsections (d)(2) and (g)(1)(A)-(B).
        "https://www.law.cornell.edu/uscode/text/26/6428#g_1",
        # Subsections (d)(2) and (g)(1)-(2).
        "https://www.law.cornell.edu/uscode/text/26/6428A#g_1",
        # Subsections (c)(2) and (e)(2)(A)-(B).
        "https://www.law.cornell.edu/uscode/text/26/6428B#e_2",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Reuse existing EITC SSN check - identical definition (SSN required)
        has_valid_ssn = person("meets_eitc_identification_requirements", period)
        # An "eligible individual" excludes "any individual with respect to
        # whom a deduction under section 151 is allowable to another
        # taxpayer" (IRC 6428(d)(2), 6428A(d)(2)) or "who is a dependent of
        # another taxpayer" (IRC 6428B(c)(2)): a claimability test.
        claimable = person("claimable_as_dependent_on_another_return", period)
        return tax_unit.sum(head_or_spouse & has_valid_ssn & ~claimable)
