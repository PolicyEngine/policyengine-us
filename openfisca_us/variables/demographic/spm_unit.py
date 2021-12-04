from openfisca_core.model_api import *
from openfisca_us.entities import *


class spm_unit_id(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Unique reference for this SPM unit"
    definition_period = ETERNITY


class spm_unit_weight(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit weight"
    definition_period = YEAR


class person_spm_unit_id(Variable):
    value_type = int
    entity = Person
    label = u"Unique reference for the SPM unit of this person"
    definition_period = ETERNITY


class is_spm_unit_head(Variable):
    value_type = bool
    entity = Person
    label = u"SPM unit head"
    definition_period = ETERNITY

    def formula(person, period, parameters):
        # Use order of input (first)
        return person.spm_unit.members_position == 0


class spm_unit_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit assets"
    definition_period = YEAR


class ccdf_income_to_smi_ratio(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Income to SMI ratio"
    definition_period = YEAR
