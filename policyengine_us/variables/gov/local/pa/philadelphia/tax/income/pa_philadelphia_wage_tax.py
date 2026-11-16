from policyengine_us.model_api import *


class pa_philadelphia_wage_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Philadelphia wage tax"
    documentation = (
        "Philadelphia employee wage or earnings tax based on explicit taxable "
        "wages and resident-status inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.phila.gov/services/payments-assistance-taxes/taxes/"
        "business-taxes/business-taxes-by-type/wage-tax-employers/"
    )
    adds = ["pa_philadelphia_wage_tax_person"]
