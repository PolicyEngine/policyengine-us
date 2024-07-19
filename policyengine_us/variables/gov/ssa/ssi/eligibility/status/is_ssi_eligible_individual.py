from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.immigration_status import ImmigrationStatus

class is_ssi_eligible_individual(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-eligible individual"
    definition_period = YEAR

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        is_ssi_eligible_spouse = person("is_ssi_eligible_spouse", period)
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        is_citizen = person("immigration_status", period) == ImmigrationStatus.CITIZEN

        return (aged_blind_disabled & ~is_ssi_eligible_spouse & (is_qualified_noncitizen | is_citizen))
