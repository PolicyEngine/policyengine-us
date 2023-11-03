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
                13850,  # this should be single amount, use fix amount as temp
            ],
        )

        standard_deduction_if_dependent = min_(
            standard_deduction,
            max_(
                std.dependent.additional_earned_income
                + tax_unit("tax_unit_earned_income", period),
                std.dependent.amount,
            ),
        )
        return standard_deduction
        # return select(
        #     [
        #         separate_filer_itemizes,
        #         claimed_as_dependent_elsewhere,
        #         True,
        #     ],
        #     [
        #         0,
        #         standard_deduction_if_dependent,
        #         standard_deduction,
        #     ],
        # )

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
                1850,  # this should be single amount, use fix amount as temp
            ],
        )
        return aged_blind_count * additional_standard_deduction_per_count

    class reform(Reform):
        def apply(self):
            self.update_variable(basic_standard_deduction)
            self.update_variable(additional_standard_deduction)

    return reform


def create_remove_standard_deduction_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_standard_deduction_head_of_household()

    p = parameters(period).gov.contrib.tax_foundation.growth_and_opportunity

    if p.remove_head_of_household is True:
        return create_remove_standard_deduction_head_of_household()
    else:
        return None


remove_standard_deduction_head_of_household = (
    create_remove_standard_deduction_head_of_household_reform(
        None, None, bypass=True
    )
)
