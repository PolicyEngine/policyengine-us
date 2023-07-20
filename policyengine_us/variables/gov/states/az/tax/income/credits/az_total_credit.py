from policyengine_us.model_api import *


# used in line2A in "Arizona Sechedule A Itemized Deduction Adjustments"
# Amount included in the "Total state income taxes on the federal Schedule A before applying the federal limitations" for which you claimed an Arizona credit
class az_total_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total Arizona credit "
    unit = USD
    documentation = "Arizona Form 140 Schedule A"
    reference = "https://azdor.gov/forms/individual/itemized-deduction-adjustments-form"
    definition_period = YEAR
    defined_for = StateCode.AZ

    # def formula(tax_unit, period, parameters):
