from policyengine_us.model_api import *


class co_medicaid_income_disregard(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid/CHP+ income disregard for Colorado"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        fpg_percent = parameters(
            period
        ).gov.hhs.medicaid.income.co_income_disregard
        fpg = tax_unit("tax_unit_fpg", period)
        return fpg * fpg_percent
