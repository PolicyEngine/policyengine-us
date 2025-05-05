from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR
    defined_for = "is_ssi_eligible_individual"

    def formula(person, period, parameters):
        # The simplest way: if you're in a marital_unit with 2 people,
        # and you are an SSI-eligible individual,
        # we say it's 'joint' no matter how much is actually deemed.
        #
        # Note: In the PolicyEngine codebase, marital units by definition only
        # include spouses (max of 2 people), not dependents or children.
        # Dependents would be in the same tax_unit or family, but not the same
        # marital_unit. Marital units are defined in entities.py as:
        # "An unmarried person, or a married and co-habiting couple."
        num_in_marriage = person.marital_unit.nb_persons()
        return num_in_marriage == 2
