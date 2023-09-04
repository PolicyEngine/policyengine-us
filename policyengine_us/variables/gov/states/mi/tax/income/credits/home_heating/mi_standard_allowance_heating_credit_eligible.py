### add FPG file path
from policyengine_us.model_api import *


class mi_standard_allowance_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Standard allowance can be claimed"
    definition_period = YEAR
    defined_for = StateCode.MI
    mi_standard_allowance_heating_credit_eligible 
   
    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating_credit.alternate_credit

    return mi_household_resources <= FPG * p.household_resources.fpg_rate 