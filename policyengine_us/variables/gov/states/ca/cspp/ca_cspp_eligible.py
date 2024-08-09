from policyengine_us.model_api import *


class ca_cspp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "California State Preschool Program eligible"
    definition_period = YEAR
    reference = (
        "https://www.ccrcca.org/headstart/programs/eligibility-requirements/"
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cspp.eligibility
        programs = add(person.tax_unit, period, p.categorical)
        living_conditions = add(person.tax_unit, period, p.living_conditions)
        income_eligible = person.tax_unit("ca_cspp_income_eligible", period)
        cspp_eligible = (
            np.any(programs) | np.any(living_conditions) | income_eligible
        )
        head_start_participating = person("head_start", period)
        return (head_start_participating > 0) & cspp_eligible
