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


class spm_unit_assets(Variable):
    value_type = float
    entity = SPMUnit
    label = u"SPM unit assets"
    definition_period = YEAR


class spm_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = u"SPM unit size"
    definition_period = YEAR
