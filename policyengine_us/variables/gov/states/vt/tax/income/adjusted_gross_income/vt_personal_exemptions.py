from policyengine_us.model_api import *


class vt_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        personal_eligibility_amount = parameters(
            period
        ).gov.states.vt.tax.income.exemption.personal

        # First, determine whether either the head or the spouse of the tax unit is claimable as a dependent in another unit.(line 5a, line5b)
        claimable_count = float(tax_unit("dsi", period))
        claimable_count += float(tax_unit("dsi_spouse", period))
        eligible_count = select(
            [
                claimable_count == 0,
                claimable_count == 1,
                claimable_count == 2,
            ],
            [2, 1, 0],
        )
        # Then, add number of other dependents claimed on federal Form 1040.(line 5c)
        eligible_count += tax_unit("tax_unit_count_dependents", period)
        return eligible_count * personal_eligibility_amount
