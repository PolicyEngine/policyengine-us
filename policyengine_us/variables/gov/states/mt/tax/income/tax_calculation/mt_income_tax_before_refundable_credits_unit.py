from policyengine_us.model_api import *
from policyengine_us.tools.mt_filing_choice import mt_separate_filing_is_cheaper


class mt_income_tax_before_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income
        indiv = add(tax_unit, period, ["mt_income_tax_before_refundable_credits_indiv"])
        joint = tax_unit("mt_income_tax_before_refundable_credits_joint", period)
        if p.married_filing_separately_on_same_return_allowed:
            return where(mt_separate_filing_is_cheaper(indiv, joint), indiv, joint)
        return joint
