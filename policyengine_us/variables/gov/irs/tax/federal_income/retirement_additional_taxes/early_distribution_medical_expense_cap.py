from policyengine_us.model_api import *


class early_distribution_medical_expense_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medical expenses above the AGI floor for the early distribution exception"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#t_2_B",
        "https://www.irs.gov/instructions/i5329",
    )

    def formula(tax_unit, period, parameters):
        # IRC 72(t)(2)(B) excepts distributions up to the amount allowable as
        # a medical deduction under section 213, whether or not the filer
        # itemizes: medical expenses above the AGI floor.
        return tax_unit("medical_expense_deduction", period)
