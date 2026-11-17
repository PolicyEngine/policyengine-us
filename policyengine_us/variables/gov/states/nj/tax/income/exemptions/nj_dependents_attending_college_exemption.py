from policyengine_us.model_api import *


class nj_dependents_attending_college_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey dependents attending college exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        # N.J.S.A. 54A:3-1.1 in the Legislature's statutes database.
        "https://lis.njleg.state.nj.us/nxt/gateway.dll?f=templates&fn=default.htm&vid=Publish:10.1048/Enu",
        # 2025 NJ-1040 instructions, line 12.
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=9",
        # IRC 152(b)(1).
        "https://uscode.house.gov/us/usc/t26/s152/",
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
        # Publication 501 excepts a return whose would-be claimant files only
        # for a refund.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
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
