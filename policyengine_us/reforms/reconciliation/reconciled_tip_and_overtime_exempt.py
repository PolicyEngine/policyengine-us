from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciled_tip_and_overtime_exempt() -> Reform:
    class tip_income_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Tip income deduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.reconciliation.tip_income_exempt
            if p.in_effect:
                person = tax_unit.members
                ssn_card_type = person("ssn_card_type", period)
                ssn_card_types = ssn_card_type.possible_values
                citizen = ssn_card_type == ssn_card_types.CITIZEN
                non_citizen_valid_ead = (
                    ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
                )
                eligible_ssn_card_type = citizen | non_citizen_valid_ead
                head = person("is_tax_unit_head", period)
                spouse = person("is_tax_unit_spouse", period)
                ineligible_head_exists = tax_unit.any(
                    head & ~eligible_ssn_card_type
                )
                ineligible_spouse_exists = tax_unit.any(
                    spouse & ~eligible_ssn_card_type
                )
                ineligible_cardholder_present = (
                    ineligible_head_exists | ineligible_spouse_exists
                )

                tip_income = person("tip_income", period)
                if p.phase_out.applies:
                    agi = tax_unit("adjusted_gross_income", period)
                    filing_status = tax_unit("filing_status", period)
                    cap = p.cap[filing_status]
                    start = p.phase_out.start[filing_status]
                    agi_excess = max_(agi - start, 0)
                    phase_out_amount = agi_excess * p.phase_out.rate
                    total_tip_income = tax_unit.sum(tip_income)
                    capped_overtime_income = min_(cap, total_tip_income)
                    phased_out_overtime_income = max_(
                        0, capped_overtime_income - phase_out_amount
                    )
                    return (
                        phased_out_overtime_income
                        * ~ineligible_cardholder_present
                    )
                eligible_ssn_card_holder = eligible_ssn_card_type & (
                    head | spouse
                )
                return tax_unit.sum(tip_income * eligible_ssn_card_holder)
            return 0

    class overtime_income_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Overtime income deduction"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.overtime_income_exempt
            if p.in_effect:
                person = tax_unit.members
                ssn_card_type = person("ssn_card_type", period)
                ssn_card_types = ssn_card_type.possible_values
                citizen = ssn_card_type == ssn_card_types.CITIZEN
                non_citizen_valid_ead = (
                    ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
                )
                eligible_ssn_card_type = citizen | non_citizen_valid_ead
                head = person("is_tax_unit_head", period)
                spouse = person("is_tax_unit_spouse", period)
                ineligible_head_exists = tax_unit.any(
                    head & ~eligible_ssn_card_type
                )
                ineligible_spouse_exists = tax_unit.any(
                    spouse & ~eligible_ssn_card_type
                )
                ineligible_cardholder_present = (
                    ineligible_head_exists | ineligible_spouse_exists
                )

                overtime_income = person("fsla_overtime_premium", period)
                if p.phase_out.applies:
                    agi = tax_unit("adjusted_gross_income", period)
                    filing_status = tax_unit("filing_status", period)
                    cap = p.cap[filing_status]
                    start = p.phase_out.start[filing_status]
                    agi_excess = max_(agi - start, 0)
                    phase_out_amount = agi_excess * p.phase_out.rate
                    total_overtime_income = tax_unit.sum(overtime_income)
                    capped_overtime_income = min_(cap, total_overtime_income)
                    phased_out_overtime_income = max_(
                        0, capped_overtime_income - phase_out_amount
                    )
                    return (
                        phased_out_overtime_income
                        * ~ineligible_cardholder_present
                    )
                eligible_ssn_card_holder = eligible_ssn_card_type & (
                    head | spouse
                )
                return tax_unit.sum(overtime_income * eligible_ssn_card_holder)
            return 0

    def modify_parameters(parameters):
        parameters.gov.irs.deductions.deductions_if_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "tip_income_deduction",
                "overtime_income_deduction",
                "itemized_taxable_income_deductions",
                "qualified_business_income_deduction",
                "wagering_losses_deduction",
            ],
        )
        parameters.gov.irs.deductions.deductions_if_not_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "tip_income_deduction",
                "overtime_income_deduction",
                "charitable_deduction_for_non_itemizers",
                "standard_deduction",
                "qualified_business_income_deduction",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(tip_income_deduction)
            self.update_variable(overtime_income_deduction)
            self.modify_parameters(modify_parameters)

    return reform


def create_reconciled_tip_and_overtime_exempt_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_tip_and_overtime_exempt()

    p = parameters.gov.contrib.reconciliation

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if (
            p(current_period).tip_income_exempt.in_effect
            or p(current_period).overtime_income_exempt.in_effect
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_tip_and_overtime_exempt()
    else:
        return None


reconciled_tip_and_overtime_exempt = (
    create_reconciled_tip_and_overtime_exempt_reform(None, None, bypass=True)
)
