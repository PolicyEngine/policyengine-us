from policyengine_us.model_api import *


class md_montgomery_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland montgomery county earned income tax credit"
    unit = USD
    documentation = "Refundable Montgomery county EITC"
    definition_period = YEAR
    reference = "https://www3.montgomerycountymd.gov/311/Solutions.aspx?SolutionId=1-4DAM0I"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.md.tax.income.credits.eitc.refundable.montgomery

        # check montgomery county match qualification
        county = tax_unit.household("county_str", period)
        in_montgomery = county == "MONTGOMERY_COUNTY_MD"

        # state EITC
        state_refundable_eitc = tax_unit("md_refundable_eitc", period)

        # apply county match
        return md_refundable_eitc * p.match * is_montgomery_resident
