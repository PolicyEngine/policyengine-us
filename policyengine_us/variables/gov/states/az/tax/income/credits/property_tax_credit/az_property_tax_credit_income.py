from policyengine_us.model_api import *


class az_property_tax_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income for the Arizona property tax the credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = "gov.states.az.tax.income.credits.property_tax.income_sources"
