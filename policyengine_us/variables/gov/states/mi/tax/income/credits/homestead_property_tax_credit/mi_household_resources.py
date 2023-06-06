from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Household Resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    adds = "gov.states.mi.tax.income.credits.homestead_property_tax_credit.household_resources"
