from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_me_ld229() -> Reform:
    class me_income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maine main income tax (before credits and supplemental tax)"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ME

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("me_taxable_income", period)
            filing_status = tax_unit("filing_status", period)
            status = filing_status.possible_values

            p = parameters(period).gov.contrib.states.me.ld229

            return select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    p.single.calc(taxable_income),
                    p.joint.calc(taxable_income),
                    p.head_of_household.calc(taxable_income),
                    p.joint.calc(taxable_income),
                    p.single.calc(taxable_income),
                ],
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(me_income_tax_before_credits)

    return reform


def create_me_ld229_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_me_ld229()

    p = parameters.gov.contrib.states.me.ld229

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_me_ld229()
    else:
        return None


me_ld229 = create_me_ld229_reform(None, None, bypass=True)
