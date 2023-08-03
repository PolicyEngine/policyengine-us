from policyengine_us.model_api import *


class spm_unit_id(Variable):
    value_type = int
    entity = SPMUnit
    label = "SPM unit ID"
    definition_period = YEAR


class person_spm_unit_id(Variable):
    value_type = int
    entity = Person
    label = "SPM unit ID"
    definition_period = YEAR
