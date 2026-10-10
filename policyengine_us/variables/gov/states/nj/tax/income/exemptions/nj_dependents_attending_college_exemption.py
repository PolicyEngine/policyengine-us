from policyengine_us.model_api import *


class nj_dependents_attending_college_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey dependents attending college exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-3-1-1/",
        # 2025 NJ-1040 instructions, line 12.
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=9",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Then get the NJ Exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.exemptions.dependents_attending_college

        # Get members in the tax unit
        person = tax_unit.members

        # Get person under 22
        is_qualifying_age = person("age", period) <= p.age_threshold

        # Get dependents in the members. The student "must be claimed as a
        # dependent on line 10 or 11" (NJ-1040 line 12), and a return on which
        # the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        is_dependent = person("is_tax_unit_dependent", period) & ~filer_is_dependent

        # Get full time students
        is_full_time_college_student = person("is_full_time_college_student", period)

        # Total number of qualifying dependents attending college
        qualifying_dependents = tax_unit.sum(
            is_dependent * is_qualifying_age * is_full_time_college_student
        )

        # Get their regular exemption amount based on their filing status.
        return qualifying_dependents * p.amount
