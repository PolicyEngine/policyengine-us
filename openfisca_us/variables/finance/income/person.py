from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class net_income(Variable):
    value_type = float
    entity = Person
    label = u"Net income"
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("is_spm_unit_head", period) * person.spm_unit(
            "SPM_unit_net_income", period
        )
