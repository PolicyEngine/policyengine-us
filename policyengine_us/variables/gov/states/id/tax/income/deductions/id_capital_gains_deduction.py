from policyengine_us.model_api import *


class id_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho capital gains deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022h/"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.capital_gains
        # taxpayer must report capital gain net income
        net_capital_gain = tax_unit("property_sales_net_capital_gain", period)

        # Ordinary Income do not qualify for the Idaho capital gains deduction
        # Gain from dispositions of certain depreciable property treated as ordinary income

        # Return calculated amount.
        return p.percentage * net_capital_gain
