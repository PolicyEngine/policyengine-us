from policyengine_us.model_api import *


class co_tabor_cash_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado TABOR cash back"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR
    reference = "https://leg.colorado.gov/sites/default/files/documents/2022A/bills/2022a_233_01.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.tabor

        joint = tax_unit("tax_unit_is_joint", period)
        return where(joint, p.joint, p.single)
