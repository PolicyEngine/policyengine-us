from policyengine_us.model_api import *


def create_remove_standard_deduction_head_of_household() -> Reform:
    class basic_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Basic Standard Deduction (Eliminating HoH)"
        unit = USD
        documentation = "The Basic standard deduction under the tax foundation growth and opportunity plan"
        definition_period = YEAR

    def formula(tax_unit, period, parameters):
        std = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        claimed_as_dependent_elsewhere = tax_unit(
            "tax_unit_dependent_elsewhere", period
        )
        if (
            parameters(
                period
            ).gov.contrib.tax_foundation.growth_and_opportunity.remove_head_of_household
            == True
        ):
            standard_deduction = select(
                [
                    filing_status == statuses.SINGLE,
                    filing_status == statuses.SEPARATE,
                    filing_status == statuses.JOINT,
                    filing_status == statuses.WIDOW,
                    filing_status == statuses.HEAD_OF_HOUSEHOLD,
                ],
                [
                    std.amount[filing_status],
                    std.amount[filing_status],
                    std.amount[filing_status],
                    std.amount[filing_status],
                    # p.head_of_household.calc(taxable_income), # this should be single amount
                ],
            )
        else:
            standard_deduction = std.amount[filing_status]

        standard_deduction_if_dependent = min_(
            standard_deduction,
            max_(
                std.dependent.additional_earned_income
                + tax_unit("tax_unit_earned_income", period),
                std.dependent.amount,
            ),
        )

        return select(
            [
                separate_filer_itemizes,
                claimed_as_dependent_elsewhere,
                True,
            ],
            [
                0,
                standard_deduction_if_dependent,
                standard_deduction,
            ],
        )

    class additional_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Additional Standard Deduction (Eliminating HoH)"
        unit = USD
        documentation = "The additional standard deduction under the tax foundation growth and opportunity plan"
        definition_period = YEAR

    def formula(tax_unit, period, parameters):
        std = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        aged_blind_count = tax_unit("aged_blind_count", period)
        if (
            parameters(
                period
            ).gov.contrib.tax_foundation.growth_and_opportunity.remove_head_of_household
            == True
        ):
            additional_standard_deduction_per_count = select(
                [
                    filing_status == statuses.SINGLE,
                    filing_status == statuses.SEPARATE,
                    filing_status == statuses.JOINT,
                    filing_status == statuses.WIDOW,
                    filing_status == statuses.HEAD_OF_HOUSEHOLD,
                ],
                [
                    std.aged_or_blind.amount[filing_status],
                    std.aged_or_blind.amount[filing_status],
                    std.aged_or_blind.amount[filing_status],
                    std.aged_or_blind.amount[filing_status],
                    # p.head_of_household.calc(taxable_income), # this should be single amount
                ],
            )
        else:
            additional_standard_deduction_per_count = std.aged_or_blind.amount[
                filing_status
            ]
        return aged_blind_count * additional_standard_deduction_per_count

    class reform(Reform):
        def apply(self):
            self.update_variable(basic_standard_deduction)

    return reform


def create_remove_standard_deduction_head_of_household(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_standard_deduction_head_of_household()

    p = parameters(period).gov.contrib.congress.delauro.american_family_act

    if p.baby_bonus > 0:
        return create_remove_standard_deduction_head_of_household()
    else:
        return None


american_family_act = create_remove_standard_deduction_head_of_household(
    None, None, bypass=True
)
