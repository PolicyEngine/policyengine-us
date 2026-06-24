from policyengine_us.model_api import *


class nj_capped_senior_freeze(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey capped Senior Freeze benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.PDF#page=3",
        "https://pub.njleg.state.nj.us/Bills/2024/PL24/88_.PDF",
        "https://lis.njleg.state.nj.us/nxt/gateway.dll?f=templates&fn=default.htm&vid=Publish:10.1048/Enu",
        "https://www.nj.gov/treasury/taxation/staynj/calculation.shtml",
        "https://www.nj.gov/treasury/taxation/ptr/index.shtml",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        anchor = tax_unit("nj_anchor", period)
        senior_freeze = tax_unit("nj_senior_freeze", period)
        return min_(senior_freeze, max_(property_taxes - anchor, 0))
