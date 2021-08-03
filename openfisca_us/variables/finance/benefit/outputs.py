from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class snap(Variable):
    value_type = float
    entity = BenefitUnit
    label = u"Supplemental Nutrition Assistance Program, benefit amount"
    definition_period = YEAR

    def formula(benefitunit, period, parameters):

        # Params:
        # Income Threshold
        # Max Benefit
        # Phase-out Rate
        # for later, Employment Rules

        # Get vars:
        # net income
        # gross income
        # number of individuals

        # Employment Status

        return standard
