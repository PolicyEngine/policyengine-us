from policyengine_us.model_api import *


class de_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware refundable EITC if claimed"
    unit = USD
    documentation = (
        "Refundable EITC credit reducing DE State income tax page 8."
    )
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.de.tax.income.credits.eitc
        return p.refundable * federal_eitc
