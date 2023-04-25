from policyengine_us.model_api import *


class ca_mental_health_services_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA mental health services tax"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ca_taxable_income", period)
        rate = parameters(
            period
        ).gov.states.ca.tax.income.mental_health_services
        return rate.calc(taxable_income)
