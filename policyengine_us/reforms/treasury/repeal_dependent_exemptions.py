from policyengine_us.model_api import *


def create_repeal_dependent_exemptions() -> Reform:
    class exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Exemptions"
        definition_period = YEAR
        documentation = "Personal exemptions amount after phase-out"
        unit = USD

        def formula(tax_unit, period, parameters):
            # calculate exemptions amount before phase-out
            exemptions = tax_unit("head_spouse_count", period)
            p = parameters(period).gov.irs.income.exemption
            amount = exemptions * p.amount
            # calculate exemptions amount after phase-out
            filing_status = tax_unit("filing_status", period)
            phase_out_start_agi = p.phase_out.start[filing_status]
            agi = tax_unit("adjusted_gross_income", period)
            excess_agi = max_(0, agi - phase_out_start_agi)
            phase_out_step_size = p.phase_out.step_size[filing_status]
            steps = excess_agi / phase_out_step_size
            phase_out_fraction = steps * p.phase_out.rate
            return max_(0, amount * (1 - phase_out_fraction))


    class reform(Reform):
        def apply(self):
            self.update_variable(exemptions)

    return reform


def create_repeal_dependent_exemptions_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_repeal_dependent_exemptions()

    p = parameters(period).gov.contrib.treasury

    if p.repeal_dependent_exemptions:
        return create_repeal_dependent_exemptions()
    else:
        return None


repeal_dependent_exemptions = create_repeal_dependent_exemptions_reform(
    None, None, bypass=True
)
