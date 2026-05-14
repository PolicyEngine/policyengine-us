from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ca_ab2591() -> Reform:
    class ca_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "California standard deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202520260AB2591",
        )
        defined_for = StateCode.CA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ca.tax.income.deductions.standard
            p_ab2591 = parameters(period).gov.contrib.states.ca.ab2591
            filing_status = tax_unit("filing_status", period)
            statuses = filing_status.possible_values

            baseline_deduction = p.amount[filing_status]

            # AB 2591 allows an election of the federal poverty line as the
            # standard deduction. For single / married-filing-separately, the
            # deduction equals the FPL for a one-person household. For head of
            # household, the FPL for a two-person household. For joint and
            # surviving-spouse filers, the FPL adjusted for the actual number of
            # persons in the household.
            p_fpg = parameters(period).gov.hhs.fpg
            state_group = tax_unit.household("state_group_str", period)
            first_person = p_fpg.first_person[state_group]
            additional_person = p_fpg.additional_person[state_group]

            household_size = tax_unit("tax_unit_size", period)
            # Bill Sec. 2, R&TC 17073.5(b)(2) sets HoH to the two-person FPL.
            # Bill Sec. 2, R&TC 17073.5(b)(1) sets single / separate to the
            # one-person FPL.
            is_joint_or_ss = (filing_status == statuses.JOINT) | (
                filing_status == statuses.SURVIVING_SPOUSE
            )
            is_hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
            fpl_household_size = where(
                is_joint_or_ss,
                household_size,
                where(is_hoh, 2, 1),
            )
            fpl_deduction = first_person + additional_person * (fpl_household_size - 1)

            # Taxpayer election: higher of FPL-based amount or baseline
            # statutory standard deduction.
            elected_deduction = max_(fpl_deduction, baseline_deduction)

            return where(p_ab2591.in_effect, elected_deduction, baseline_deduction)

    class reform(Reform):
        def apply(self):
            self.update_variable(ca_standard_deduction)

    return reform


def create_ca_ab2591_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ca_ab2591()

    p = parameters.gov.contrib.states.ca.ab2591

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ca_ab2591()
    else:
        return None


ca_ab2591 = create_ca_ab2591_reform(None, None, bypass=True)
