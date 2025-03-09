# File: policyengine_us/variables/gov/ssa/ssi/ssi_claim_is_joint.py
from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR

    def formula(person, period, parameters):
        # The simplest way: if you're in a marital_unit with 2 people,
        # and you are an SSI-eligible individual,
        # we say it's 'joint' no matter how much is actually deemed.
        is_eligible = person("is_ssi_eligible_individual", period)
        num_in_marriage = person.marital_unit.nb_persons()
        return (num_in_marriage == 2) & is_eligible
