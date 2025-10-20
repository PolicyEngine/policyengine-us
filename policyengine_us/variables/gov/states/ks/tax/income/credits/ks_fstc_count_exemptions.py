from policyengine_us.model_api import *


class ks_fstc_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "number of Kansas exemptions for the food sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.kansas.gov/kdor/webfile/help/modal-food-sales-credit-details.html"
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        joint = tax_unit("tax_unit_is_joint", period)
        # The additional head of household exemption does not apply
        adults = where(joint, 2, 1)
        dependents = tax_unit("tax_unit_dependents", period)
        return adults + dependents
