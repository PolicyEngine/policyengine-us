from openfisca_tools.model_api import *
from openfisca_us.entities import *


class household_net_income(Variable):
    value_type = float
    entity = Household
    label = u"Household net income"
    definition_period = YEAR

    def formula(household, period, parameters):
        return household.sum(household.members("net_income", period))
