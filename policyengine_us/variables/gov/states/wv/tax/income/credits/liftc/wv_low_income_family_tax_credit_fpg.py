from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_fpg(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Federal poverty guidelines for the West Virginia low-income family tax credit"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-22A/"
    defined_for = "wv_low_income_family_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.credits.liftc  # low_income_family_tax_credit

        # W. Va. Code 11-21-22A: family size is "the total number of exemptions
        # that may be legally claimed", not the number of people in the unit.
        # A filer who can be claimed as a dependent has no exemption, and a
        # return where either filer can be has no dependent exemptions.
        n = tax_unit("exemptions_count", period)
        state_group = tax_unit.household("state_group_str", period)

        p_fpg = parameters(period).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group]
        pn = p_fpg.additional_person[state_group]
        family_size = min_(n, p.max_family_size)
        return p1 + pn * (family_size - 1)
