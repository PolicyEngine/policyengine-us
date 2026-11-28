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
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nd.tax.income.taxable_income.subtractions
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        # The instructions say the child must qualify as a federal dependent.
        # N.D.C.C. 57-38-30.3(2)(p) imposes no dependency condition.
        return stillborn * p.stillborn
