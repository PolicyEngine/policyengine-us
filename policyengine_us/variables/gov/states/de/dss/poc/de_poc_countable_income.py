from policyengine_us.model_api import *


class de_poc_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware Purchase of Care countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.DE
    reference = "https://regulations.delaware.gov/AdminCode/title16/Department%20of%20Health%20and%20Social%20Services/Division%20of%20Social%20Services/11003.shtml"

    adds = "gov.states.de.dss.poc.income.countable_income.sources"
