from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_pa_ctc_flat_amount() -> Reform:
    class pa_ctc_flat_amount(Variable):
        value_type = float
        entity = TaxUnit
        label = "Pennsylvania flat amount Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.PA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.pa.ctc.flat_amount

            # Count eligible children (under age limit)
            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            eligible = is_dependent & (age < p.age_limit)
            eligible_children = tax_unit.sum(eligible)

            # Calculate maximum credit
            max_credit = eligible_children * p.amount

            # Apply phaseout based on AGI and filing status
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)
            threshold = p.phaseout.threshold[filing_status]
            rate = p.phaseout.rate

            # Calculate phaseout reduction
            excess_income = max_(agi - threshold, 0)
            reduction = excess_income * rate

            return max_(max_credit - reduction, 0)

    def modify_parameters(parameters):
        # Add pa_ctc_flat_amount to refundable credits list
        refundable = parameters.gov.states.pa.tax.income.credits.refundable
        current_refundable = refundable(instant("2026-01-01"))
        if "pa_ctc_flat_amount" not in current_refundable:
            new_refundable = list(current_refundable) + ["pa_ctc_flat_amount"]
            refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=new_refundable,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(pa_ctc_flat_amount)
            self.modify_parameters(modify_parameters)

    return reform


def create_pa_ctc_flat_amount_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_pa_ctc_flat_amount()

    p = parameters.gov.contrib.states.pa.ctc.flat_amount

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_pa_ctc_flat_amount()
    else:
        return None


pa_ctc_flat_amount = create_pa_ctc_flat_amount_reform(None, None, bypass=True)
