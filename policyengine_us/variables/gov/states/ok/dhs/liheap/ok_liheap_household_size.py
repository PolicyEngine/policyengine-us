from policyengine_us.model_api import *


class ok_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Oklahoma LIHEAP eligible household size"
    defined_for = StateCode.OK
    # OAC 340:20-1-10(h)(3): exclude ineligible aliens from both the
    # financial standard and benefit size; their income follows deeming.
    reference = "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html"
    # SPM membership represents the economic unit sharing heating costs.
    # SSN furnishing/application and shared-meter household facts are
    # not represented by the available inputs.
    adds = ["ok_liheap_immigration_eligible"]
