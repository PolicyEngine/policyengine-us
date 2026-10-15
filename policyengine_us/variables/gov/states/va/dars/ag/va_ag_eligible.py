from policyengine_us.model_api import *


class va_ag_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Virginia Auxiliary Grant non-income eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    # PDF pages 75-78, 93-96, 102-103, 125, 152
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
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        resource_eligible = receives_ssi | (
            resources <= where(joint, limits.couple, limits.individual)
        )
        # Chapter C 8.2.2: an applicant who appears to meet SSI income standards
        # must apply for SSI, and 8.2.2.2.1 denies AG otherwise; 8.2.1 exempts
        # an applicant over income for SSI.
        pursues_ssi = person("takes_up_ssi_if_eligible", period.this_year) | (
            person("uncapped_ssi", period) <= 0
        )
        return (
            person("va_ag_certified", period)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & (citizen | immigrant)
            & resource_eligible
            & ~person("is_incarcerated", period)
            & pursues_ssi
        )
