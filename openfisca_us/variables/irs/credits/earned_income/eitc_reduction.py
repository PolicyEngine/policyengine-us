from openfisca_us.model_api import *


class eitc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#a_2"

    def formula(tax_unit, period, parameters):
        eitc = parameters(period).irs.credits.eitc
        earnings = tax_unit("filer_earned", period)
        highest_income_variable = max_(
            earnings, tax_unit("adjusted_gross_income", period)
        )
        is_joint = tax_unit("tax_unit_is_joint", period)
        num_children = tax_unit.sum(tax_unit.members("is_child", period))
        phaseout_start = (
            eitc.phaseout.start.calc(num_children)
            + is_joint * eitc.phaseout.joint_bonus
        )
        phaseout_rate = eitc.phaseout.rate.calc(num_children)
        phaseout_region = max_(0, highest_income_variable - phaseout_start)
        uncapped_reduction = phaseout_rate * phaseout_region
        return min_(uncapped_reduction, tax_unit("eitc_maximum", period))
