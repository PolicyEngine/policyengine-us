from policyengine_us.model_api import *


class nd_stillborn_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota stillborn child subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ND
    reference = (
        "https://ndlegis.gov/cencode/t57c38.pdf#nameddest=57-38-30p3",
        # 2025 Schedule ND-1SA instructions, line 8.
        "https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2025-iit/28710-schedule-nd-1sa-2025.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.income.taxable_income.subtractions
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        # Schedule ND-1SA allows the deduction only if "You would have been
        # eligible to claim the child as a dependent on your ... federal
        # income tax return if the child had been born alive", and a return
        # on which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(filer_is_dependent, 0, stillborn * p.stillborn)
