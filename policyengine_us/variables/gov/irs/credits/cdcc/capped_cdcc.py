from policyengine_us.model_api import *


class capped_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped Child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        expenses = tax_unit("cdcc_relevant_expenses", period)
        rate = tax_unit("cdcc_rate", period)
        # The cdcc is capped at the amount of Form 1040, line 18
        tax_before_credits = tax_unit("regular_tax_before_credits", period)
        # reduced by the foreign tax credit
        foreign_tax_credit = tax_unit("foreign_tax_credit", period)
        # The tax before credits amount is also reduced by the Partner’s Additional Reporting Year Tax
        # which is currently not implemented
        cap = max_(tax_before_credits - foreign_tax_credit, 0)
        return min_(expenses * rate, cap)
