from policyengine_us.model_api import *


class ok_federal_eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Federal earned income credit for the Oklahoma EITC computation"
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    unit = USD
    defined_for = "ok_federal_eitc_eligible"

    def formula(tax_unit, period, parameters):
        takes_up_eitc = tax_unit("takes_up_eitc", period)
        maximum = tax_unit("ok_federal_eitc_maximum", period)
        phased_in = tax_unit("ok_federal_eitc_phased_in", period)
        reduction = tax_unit("ok_federal_eitc_reduction", period)
        limitation = max_(0, maximum - reduction)
        return min_(phased_in, limitation) * takes_up_eitc
