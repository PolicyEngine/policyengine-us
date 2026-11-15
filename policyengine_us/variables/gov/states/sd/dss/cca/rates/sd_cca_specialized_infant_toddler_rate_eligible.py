from policyengine_us.model_api import *


class sd_cca_specialized_infant_toddler_rate_eligible(Variable):
    value_type = bool
    entity = Person
    default_value = False
    definition_period = MONTH
    defined_for = StateCode.SD
    label = "South Dakota CCA provider qualifies for the specialized infant and toddler rate"
    documentation = "Records whether a registered family child care provider qualifies for the specialized rate by registering to care for six or fewer children. DSS limits this rate to children under age three in its July 2024 Family Child Care rate sheet."
    reference = "https://dss.sd.gov/docs/childcare/assistance/Reimbursement_Rates/Family_Child_Care.pdf"
