from policyengine_us.model_api import *


class nj_property_tax_relief(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax relief benefits"
    unit = USD
    definition_period = YEAR
    documentation = "Combined New Jersey property tax relief, including Stay NJ and Senior Freeze/PTR relief under N.J.S.A. 54:4-8.67 et seq."
    reference = (
        "https://pub.njleg.state.nj.us/Bills/2022/PL23/75_.PDF#page=3",
        "https://pub.njleg.state.nj.us/Bills/2024/PL24/88_.PDF",
        "https://lis.njleg.state.nj.us/nxt/gateway.dll?f=templates&fn=default.htm&vid=Publish:10.1048/Enu",
        "https://www.nj.gov/treasury/taxation/relief.shtml",
        "https://www.nj.gov/treasury/taxation/staynj/calculation.shtml",
    )
    defined_for = StateCode.NJ

    def formula_2026(tax_unit, period, parameters):
        return (
            tax_unit("nj_anchor", period)
            + tax_unit("nj_capped_senior_freeze", period)
            + tax_unit("nj_staynj", period)
        )
