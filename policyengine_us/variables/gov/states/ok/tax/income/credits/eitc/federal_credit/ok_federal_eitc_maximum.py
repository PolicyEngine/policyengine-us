from policyengine_us.model_api import *


class ok_federal_eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum federal EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    unit = USD
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        eitc = parameters(f"2020-01-01").gov.irs.credits.eitc
        return eitc.max.calc(child_count)
