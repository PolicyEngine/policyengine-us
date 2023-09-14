from policyengine_us.model_api import *

class property_tax_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho property tax net capital gain"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/regulation/idaho-administrative-code/title-idapa-35-tax-commission-state/rule-350101-income-tax-administrative-rules/section-350101170-idaho-capital-gains-deduction-in-general"
    defined_for = StateCode.ID