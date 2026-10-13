from policyengine_us.model_api import *


class va_ag_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Virginia Auxiliary Grant non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    # PDF pages 75-78, 93, 125, 152
    reference = "https://townhall.virginia.gov/l/GetFile.cfm?File=C:%5CTownHall%5Cdocroot%5CGuidanceDocs%5C262%5CGDoc_DARS_5346_v2.pdf#page=75"

    def formula(person, period, parameters):
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        immigrant = person("is_ssi_qualified_noncitizen", period.this_year)
        joint = (
            person.marital_unit.sum(person("va_ag_is_joint_initial_month", period)) == 2
        )
        resources = person("ssi_countable_resources", period.this_year)
        resources = where(joint, person.marital_unit.sum(resources), resources)
        limits = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        resource_eligible = (person("ssi", period) > 0) | (
            resources <= where(joint, limits.couple, limits.individual)
        )
        return (
            person("va_ag_certified", period)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & (citizen | immigrant)
            & resource_eligible
            & ~person("is_incarcerated", period)
        )
