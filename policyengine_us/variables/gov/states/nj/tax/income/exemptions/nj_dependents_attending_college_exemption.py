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

        # get members in the tax unit
        person = tax_unit.members

        # get dependents in the members
        is_dependent = person("is_tax_unit_dependent", period)

        # get person under 22
        qualifying_age = person("age", period) <= p.age_threshold

        # get full time students
        full_time_student = person("is_full_time_student", period)

        # Get their regular exemption amount based on their filing status.
        return (
            tax_unit.sum(is_dependent * full_time_student * qualifying_age)
            * p.amount
        )
