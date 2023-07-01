from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        income_eligible = tax_unit("nh_income_tax", period) > 0
        base = parameters(
            period
        ).gov.states.nh.tax.income.exemptions.amount.base
        return income_eligible * base[filing_status]
