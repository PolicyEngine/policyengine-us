from policyengine_us.model_api import *


class md_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Browse/Home/Maryland/MarylandCodeCourtRules?guid=NAE804370A64411DBB5DDAC3692B918BC&transitionType=Default&contextData=%28sc.Default%29"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        us_agi = tax_unit("adjusted_gross_income", period)
        md_adds = tax_unit("md_total_additions", period)
        md_subs = tax_unit("md_total_subtractions", period)
        return max_(0, us_agi + md_adds - md_subs)
