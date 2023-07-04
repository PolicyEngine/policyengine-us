from policyengine_us.model_api import *
from numpy import invert


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
        # Then, determine whether either the head or the spouse of the tax unit is claimable as a dependent in another unit.
        claimable_elsewhere_head = tax_unit("dsi", period)
        claimable_elsewhere_spouse = tax_unit("dsi_spouse", period)
        # If claimable elsewhere, it is not eligible for vt personal exemption (line 5a, line 5b)
        eligible_head = invert(claimable_elsewhere_head).astype(int)
        eligible_spouse = invert(claimable_elsewhere_spouse).astype(int)
        eligible_count = where(
            is_joint, (eligible_head + eligible_spouse), eligible_head
        )
        # Last, add number of other dependents claimed on federal Form 1040.(line 5c)
        total_exemption_count = eligible_count + tax_unit(
            "tax_unit_count_dependents", period
        )
        return total_exemption_count * personal_eligibility_amount
