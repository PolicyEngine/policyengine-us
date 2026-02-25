from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ct_sb100() -> Reform:
    class ct_income_tax_after_personal_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Connecticut income tax after personal tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.CT

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("ct_taxable_income", period)
            filing_status = tax_unit("filing_status", period)
            status = filing_status.possible_values

            # Standard CT rates
            p = parameters(period).gov.states.ct.tax.income.rates

            # SB-100 reduced rates for qualifying taxpayers
            sb100 = parameters(period).gov.contrib.states.ct.sb100
            sb100_rates = sb100.rates

            # Calculate tax using standard rates
            standard_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    p.single.calc(taxable_income),
                    p.joint.calc(taxable_income),
                    p.separate.calc(taxable_income),
                    p.surviving_spouse.calc(taxable_income),
                    p.head_of_household.calc(taxable_income),
                ],
            )

            # Calculate tax using SB-100 reduced rates
            sb100_tax = select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.SEPARATE,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                ],
                [
                    sb100_rates.single.calc(taxable_income),
                    sb100_rates.joint.calc(taxable_income),
                    sb100_rates.separate.calc(taxable_income),
                    sb100_rates.surviving_spouse.calc(taxable_income),
                    sb100_rates.head_of_household.calc(taxable_income),
                ],
            )

            # Determine eligibility based on AGI threshold
            agi = tax_unit("adjusted_gross_income", period)
            income_threshold = sb100.income_threshold[filing_status]
            qualifies = agi < income_threshold

            # Use SB-100 rates if qualifying, otherwise standard rates
            itax_before_personal_credits = where(
                qualifies, sb100_tax, standard_tax
            )

            # Apply add-backs and recaptures
            add_back = tax_unit("ct_income_tax_phase_out_add_back", period)
            tax_recapture = tax_unit("ct_income_tax_recapture", period)
            total = itax_before_personal_credits + add_back + tax_recapture

            # Apply personal credit
            personal_credit_rate = tax_unit("ct_personal_credit_rate", period)
            personal_credit_amount = personal_credit_rate * total

            return max_(0, total - personal_credit_amount)

    class reform(Reform):
        def apply(self):
            self.update_variable(ct_income_tax_after_personal_credits)

    return reform


def create_ct_sb100_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ct_sb100()

    p = parameters.gov.contrib.states.ct.sb100

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ct_sb100()
    else:
        return None


ct_sb100 = create_ct_sb100_reform(None, None, bypass=True)
