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
        # First, Need to determine the tax unit filing status, if they are filing jointly
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        # Then, determine whether either the head or the spouse of the tax unit is claimable as a dependent in another unit.(line 5a, line 5b)
        claimable_head = (tax_unit("dsi", period)).astype(int)
        claimable_spouse = (tax_unit("dsi_spouse", period)).astype(int)
        claimable_count = claimable_head + claimable_spouse
        eligible_count = select(
            [
                (claimable_count == 0 & is_joint),
                (claimable_count == 1 & is_joint),
                (claimable_count == 2 & is_joint),
                (claimable_count == 0 & ~is_joint),
                (claimable_count == 1 & ~is_joint),
            ],
            [2, 1, 0, 1, 0],
        )
        # Last, add number of other dependents claimed on federal Form 1040.(line 5c)
        total_exemption_count = eligible_count + tax_unit(
            "tax_unit_count_dependents", period
        )
        return total_exemption_count * personal_eligibility_amount
