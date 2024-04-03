from policyengine_us.model_api import *


class nd_military_pay_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota military pay exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    reference = "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2023-iit/2023-individual-income-tax-booklet.pdf#page=15"

    def formula(tax_unit, period, parameters):
        military_pay = add(tax_unit, period, ["military_service_income"])
        return military_pay
