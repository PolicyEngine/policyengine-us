from policyengine_us.model_api import *


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/63#c_2"

    def formula(tax_unit, period, parameters):
        std = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        claimed_as_dependent_elsewhere = tax_unit(
            "tax_unit_dependent_elsewhere", period
        )
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
