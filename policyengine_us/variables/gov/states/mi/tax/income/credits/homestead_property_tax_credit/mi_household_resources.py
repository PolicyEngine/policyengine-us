from policyengine_us.model_api import *


class mi_household_resources(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan household resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = ("http://legislature.mi.gov/doc.aspx?mcl-206-508",)
    adds = "gov.states.mi.tax.income.credits.homestead_property_tax_credit.household_resources"
