from policyengine_core.periods import period as period_
from policyengine_us.model_api import *


def create_me_ld229() -> Reform:
    class me_income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maine main income tax before credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ME
        reference = "https://legislature.maine.gov/backend/App/services/getDocument.aspx?documentId=119704"

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("me_taxable_income", period)
            filing_status = tax_unit("filing_status", period)
            status = filing_status.possible_values

            baseline_rates = parameters(period).gov.states.me.tax.income.main
            reform_parameters = parameters(period).gov.contrib.states.me.ld229
            reform_in_effect = reform_parameters.in_effect
            reform_rates = reform_parameters.rates

            baseline_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    baseline_rates.single.calc(taxable_income),
                    baseline_rates.joint.calc(taxable_income),
                    baseline_rates.head_of_household.calc(taxable_income),
                    baseline_rates.surviving_spouse.calc(taxable_income),
                    baseline_rates.separate.calc(taxable_income),
                ],
            )

            reform_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    reform_rates.single.calc(taxable_income),
                    reform_rates.joint.calc(taxable_income),
                    reform_rates.head_of_household.calc(taxable_income),
                    reform_rates.surviving_spouse.calc(taxable_income),
                    reform_rates.separate.calc(taxable_income),
                ],
            )

            return where(reform_in_effect, reform_tax, baseline_tax)

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

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_me_ld229()
    else:
        return None


me_ld229 = create_me_ld229_reform(None, None, bypass=True)
