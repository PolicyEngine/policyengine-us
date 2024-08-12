from policyengine_us.model_api import *


class ca_ccrc_head_start_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California Child Care Resource Center Head Start eligible"
    definition_period = YEAR
    reference = (
        "https://www.ccrcca.org/headstart/programs/eligibility-requirements/"
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.ccrc.head_start.eligibility
        qualifying_programs = add(
            person.tax_unit, period, p.qualifying_programs
        )
        living_conditions = add(person.tax_unit, period, p.living_conditions)
        income_eligible = person.tax_unit(
            "ca_ccrc_head_start_income_eligible", period
        )
        return (
            np.any(qualifying_programs)
            | np.any(living_conditions)
            | income_eligible
        )
