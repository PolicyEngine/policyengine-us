from policyengine_us.model_api import *


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/63#c_2"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.standard
        filing_status = tax_unit("filing_status", period)
        separate_filer_itemizes = tax_unit("separate_filer_itemizes", period)
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        standard_deduction = p.amount[filing_status]
        standard_deduction_if_dependent = min_(
            standard_deduction,
            max_(
                p.dependent.additional_earned_income
                + tax_unit("tax_unit_earned_income", period),
                p.dependent.amount,
            ),
        )
        return select(
            [
                separate_filer_itemizes,
                dependent_elsewhere,
            ],
            [
                0,
                standard_deduction_if_dependent,
            ],
            default=standard_deduction,
        )
