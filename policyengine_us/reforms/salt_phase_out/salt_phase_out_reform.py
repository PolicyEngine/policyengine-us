from policyengine_us.model_api import *


def create_salt_phase_out() -> Reform:
    class salt_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "SALT deduction"
        unit = USD
        documentation = "State and local taxes plus real estate tax deduction from taxable income."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/164"

        def formula(tax_unit, period, parameters):
            salt_amount = add(
                tax_unit,
                period,
                ["state_and_local_sales_or_income_tax", "real_estate_taxes"],
            )
            p = parameters(
                period
            ).gov.irs.deductions.itemized.salt_and_real_estate
            filing_status = tax_unit("filing_status", period)
            cap = p.cap[filing_status]
            p_ref = parameters(period).gov.contrib.salt_phase_out
            income = tax_unit("adjusted_gross_income", period)
            joint = filing_status == filing_status.possible_values.JOINT
            phase_out = where(
                joint,
                p_ref.rate.joint.calc(income),
                p_ref.rate.other.calc(income),
            )
            capped_salt = min_(cap, salt_amount)
            return max_(0, capped_salt - phase_out)

    class reform(Reform):
        def apply(self):
            self.update_variable(salt_deduction)

    return reform


def create_salt_phase_out_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_salt_phase_out()

    p = parameters(period).gov.contrib.salt_phase_out

    if p.in_effect:
        return create_salt_phase_out()
    else:
        return None


salt_phase_out_reform = create_salt_phase_out_reform(None, None, bypass=True)
