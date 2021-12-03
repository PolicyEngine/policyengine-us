from openfisca_core.model_api import *
from openfisca_us.entities import *


class provider_type_group(Variable):
    value_type = Enum
    possible_values = ProviderTypeGroup
    # DCC_SACC is most common among provider types
    default_value = ProviderTypeGroup.DCC_SACC
    entity = Person
    label = u"CCDF provider type group"
    definition_period = YEAR


class childcare_hours_per_week(Variable):
    value_type = float
    entity = Person
    label = u"Child care hours per week"
    definition_period = YEAR


class childcare_hours_per_day(Variable):
    value_type = float
    entity = Person
    label = u"Child care hours per day"
    definition_period = YEAR


class childcare_days_per_week(Variable):
    value_type = float
    entity = Person
    label = u"Child care days per week"
    definition_period = YEAR
