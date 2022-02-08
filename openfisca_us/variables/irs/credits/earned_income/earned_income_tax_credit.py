from openfisca_us.model_api import *


class earned_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "EITC"
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
    unit = USD

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("eitc_eligible", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        return eligible * (maximum - reduction)


c59660 = variable_alias("c59660", earned_income_tax_credit)
eitc = variable_alias("eitc", earned_income_tax_credit)
