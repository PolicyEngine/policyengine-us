from policyengine_us.model_api import *


class is_barred_from_american_opportunity_credit_due_to_improper_claims(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Barred from American Opportunity Credit due to improper claims"
    documentation = "Whether the taxpayer is barred from the American Opportunity Credit due to prior fraudulent, reckless, intentional-disregard, or deficiency-denied claims."
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"
