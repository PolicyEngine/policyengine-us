from policyengine_us.model_api import *


class interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest deduction"
    unit = USD
    documentation = (
        "Mortgage and investment interest the head and spouse deduct from "
        "taxable income. A dependent's own interest belongs on the "
        "dependent's return."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/163"

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_add(tax_unit, period, ["deductible_interest_expense"])
