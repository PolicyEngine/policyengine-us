from policyengine_us.model_api import *


class nj_dependents_attending_college_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey dependents attending college exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Then get the NJ Exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.exemptions.dependents_attending_college

        # Get members in the tax unit
        person = tax_unit.members

        # Get person under 22
        dependent_age = person("age", period) <= p.age_threshold

        # Get dependents in the members
        is_dependent = person("is_tax_unit_dependent", period)

        # Get full time students
        full_time_student = person("is_full_time_student", period)

        # Total number of qualifying dependents attending college
        qualifying_dependents = tax_unit.sum(
            is_dependent * dependent_age * full_time_student
        )

        # Get their regular exemption amount based on their filing status.
        return qualifying_dependents * p.amount
