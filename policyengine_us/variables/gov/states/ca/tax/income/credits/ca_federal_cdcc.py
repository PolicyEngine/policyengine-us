from policyengine_us.model_api import *


class ca_federal_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Child and Dependent Care Expenses Credit"
    unit = USD
    documentation = ""
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):

        ca_expenses = tax_unit("ca_cdcc_relevant_expenses", period) 
        ca_rate = tax_unit("ca_cdcc_rate", period)

        return ca_expenses*ca_rate
