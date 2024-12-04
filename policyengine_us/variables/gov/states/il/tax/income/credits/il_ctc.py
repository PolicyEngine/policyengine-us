from policyengine_us.model_api import *


class il_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ilga.gov/legislation/fulltext.asp?DocName=&SessionId=112&GA=103&DocTypeId=HB&DocNum=4917&GAID=17&LegID=152789&SpecSess=&Session="
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        earned_income = tax_unit("tax_unit_earned_income", period)
        agi = tax_unit("adjusted_gross_income", period)
        larger_income = max_(earned_income, agi)
        p = parameters(period).gov.states.il.tax.income.credits.ctc
        children = tax_unit("ctc_qualifying_children", period)
        base_amount = p.amount * children
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        phase_out = where(
            joint,
            p.reduction.joint.calc(larger_income),
            p.reduction.other.calc(larger_income),
        )
        return max_(base_amount - phase_out, 0)
