from policyengine_us.model_api import *


class md_montgomery_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montgomery County, Maryland EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www3.montgomerycountymd.gov/311/Solutions.aspx?SolutionId=1-4DAM0I"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.md.montgomery.tax.income.credits.eitc.refundable

        # Check whether unit is in montgomery county
        county = tax_unit.household("county_str", period)
        in_montgomery = county == "MONTGOMERY_COUNTY_MD"

        # state EITC
        state_refundable_eitc = tax_unit("md_refundable_eitc", period)

        # apply county match
        return state_refundable_eitc * p.match * in_montgomery
