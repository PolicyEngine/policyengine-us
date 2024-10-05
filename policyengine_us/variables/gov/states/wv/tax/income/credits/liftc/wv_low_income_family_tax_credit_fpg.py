from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal poverty guidelines for the West Virginia low-income family tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "wv_low_income_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.credits.liftc  # low_income_family_tax_credit

        # max family size limit
        n = tax_unit("tax_unit_size", period)
        state_group = tax_unit.household("state_group", period)

        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        family_size = min_(n, p.max_family_size)
        return p1 + pn * (family_size - 1)
