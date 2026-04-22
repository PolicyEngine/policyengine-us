from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_mn_hf4890() -> Reform:
    class mn_basic_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota basic tax calculated using HF4890 tax rate schedules"
        unit = USD
        definition_period = YEAR
        reference = "https://www.revisor.mn.gov/bills/94/2026/0/HF/4890/versions/0/"
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            filing_status = tax_unit("filing_status", period)
            statuses = filing_status.possible_values
            taxable_income = tax_unit("mn_taxable_income", period)

            baseline_rates = parameters(period).gov.states.mn.tax.income.rates
            hf4890 = parameters(period).gov.contrib.states.mn.hf4890
            hf4890_rates = hf4890.rates

            baseline_tax = select(
                [
                    filing_status == statuses.SINGLE,
                    filing_status == statuses.SEPARATE,
                    filing_status == statuses.JOINT,
                    filing_status == statuses.SURVIVING_SPOUSE,
                    filing_status == statuses.HEAD_OF_HOUSEHOLD,
                ],
                [
                    baseline_rates.single.calc(taxable_income),
                    baseline_rates.separate.calc(taxable_income),
                    baseline_rates.joint.calc(taxable_income),
                    baseline_rates.surviving_spouse.calc(taxable_income),
                    baseline_rates.head_of_household.calc(taxable_income),
                ],
            )

            hf4890_tax = select(
                [
                    filing_status == statuses.SINGLE,
                    filing_status == statuses.SEPARATE,
                    filing_status == statuses.JOINT,
                    filing_status == statuses.SURVIVING_SPOUSE,
                    filing_status == statuses.HEAD_OF_HOUSEHOLD,
                ],
                [
                    hf4890_rates.single.calc(taxable_income),
                    hf4890_rates.separate.calc(taxable_income),
                    hf4890_rates.joint.calc(taxable_income),
                    hf4890_rates.surviving_spouse.calc(taxable_income),
                    hf4890_rates.head_of_household.calc(taxable_income),
                ],
            )

            return where(hf4890.in_effect, hf4890_tax, baseline_tax)

    class reform(Reform):
        def apply(self):
            self.update_variable(mn_basic_tax)

    return reform


def create_mn_hf4890_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mn_hf4890()

    p = parameters.gov.contrib.states.mn.hf4890

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mn_hf4890()
    else:
        return None


mn_hf4890 = create_mn_hf4890_reform(None, None, bypass=True)
