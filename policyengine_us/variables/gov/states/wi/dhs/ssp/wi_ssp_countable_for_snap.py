from policyengine_us.model_api import *


class wi_ssp_countable_for_snap(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin state SSI supplements countable for FoodShare"
    definition_period = MONTH
    unit = USD
    reference = "https://www.emhandbooks.wisconsin.gov/fsh/policy_files/4/43/4.3.4.htm"
    # The current FoodShare income manual explicitly excludes SSI-E.
    # The SSI-E handbook's older FoodShare discussion says otherwise;
    # use the administering program's current, specific income rule.
    adds = ["wi_ssp_regular", "wi_cts"]
