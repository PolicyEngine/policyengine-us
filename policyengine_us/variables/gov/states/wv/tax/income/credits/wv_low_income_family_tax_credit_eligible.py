from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia low-income family tax credit"
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        # modified agi needed to be modified
        wv_agi = tax_unit("wv_agi", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(
            period
        ).gov.states.wv.tax.income.credits.low_income_family_tax_credit

        # max family size limit
        n = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group_str", period)
        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        family_size = min_(n, p.max_family_size)
        fpg = p1 + pn * (family_size - 1)

        # n = tax_unit("tax_unit_size", period)
        # tax_unit = min_(n, p.max_family_size)
        # fpg = tax_unit("tax_unit_fpg", period)
        # tax_unit is a function how to calculate tax_unit_fpg for the max family size

        # modified agi limit
        fpg_amount = p.fpg_percent[filing_status] * fpg
        income_threshold = p.income_threshold[filing_status] + fpg_amount
        return wv_agi <= income_threshold
