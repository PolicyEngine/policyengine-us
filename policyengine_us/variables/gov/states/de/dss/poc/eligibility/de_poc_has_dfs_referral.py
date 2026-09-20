from policyengine_us.model_api import *


class de_poc_has_dfs_referral(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    defined_for = StateCode.DE
    label = "Delaware DFS child-care referral"
    documentation = "Whether the child has an active DFS case and a DFS referral authorizing protective child care under DSSM 11003.7.8(D). General court supervision or an unmet protective need alone does not establish this referral."
    reference = "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=79"
