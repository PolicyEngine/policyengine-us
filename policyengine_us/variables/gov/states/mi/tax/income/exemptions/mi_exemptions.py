from policyengine_us.model_api import *


class mi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan exemptions"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-30",
        "https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=10",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mi.tax.income.exemptions

        # Personal Exemptions & Stillborn Exemptions
        personal_exemption = tax_unit("mi_personal_exemptions", period)

        # Disabled exemptions
        disabled_people = add(
            tax_unit, period, ["mi_disabled_exemption_eligible_person"]
        )
        disabled_exemption = disabled_people * p.disabled.amount.base

        # Disabled veteran exemptions
        disabled_veterans = add(
            tax_unit, period, ["is_fully_disabled_service_connected_veteran"]
        )
        disabled_veteran_exemption = disabled_veterans * p.disabled.amount.veteran

        # MCL 206.30(4): an individual who can be claimed as a dependent on
        # another return gets no personal exemption but subtracts $1,500.
        # Treasury's instructions do not address a joint return where only
        # one spouse can be claimed; since subsection (4) speaks of an
        # individual, we apply it to each spouse, so the other keeps their own
        # personal exemption (and any stillbirth exemption). A joint return on
        # which either spouse can be claimed generally claims no dependents
        # (IRS Publication 501, "Dependent Taxpayer Test"; its exception for a
        # claimer who files only for a refund is not modeled).
        filers = add(tax_unit, period, ["is_tax_unit_head_or_spouse"])
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        dependent_filers = filers - independent_filers
        stillborn = tax_unit("tax_unit_stillborn_children", period)
        independent_filer_exemptions = (
            independent_filers + where(independent_filers > 0, stillborn, 0)
        ) * p.personal
        dependent_filer_exemptions = dependent_filers * p.dependent_on_other_return

        # Total exemptions
        return (
            where(
                dependent_filers > 0,
                independent_filer_exemptions + dependent_filer_exemptions,
                personal_exemption,
            )
            + disabled_exemption
            + disabled_veteran_exemption
        )
