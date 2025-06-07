from policyengine_us.model_api import *


class farm_income(Variable):
    value_type = float
    entity = Person
    label = "farm income"
    unit = USD
    documentation = "Income averaging for farmers and fishermen. Schedule J. Seperate from QBI and self-employment income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1301"
    uprating = "calibration.gov.irs.soi.farm_income"
