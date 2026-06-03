from policyengine_us.model_api import *


class ca_marin_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Marin County General Relief"
    definition_period = MONTH
    defined_for = "in_marin"
    reference = (
        "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=11",
        "https://hhs.marincounty.gov/services/get-cash-assistance-myself-general-relief/general-relief-cash-assistance",
    )

    def formula(spm_unit, period, parameters):
        # GR is limited to adults with no dependents (or <50% custody) per Marin
        # HHS; we don't model the dependent-status gate at the moment (matches
        # LA County GR).
        age_eligible = spm_unit("ca_marin_general_relief_age_eligible", period)
        immigration_eligible = spm_unit(
            "ca_marin_general_relief_immigration_status_eligible", period
        )
        liquid_asset_eligible = spm_unit(
            "ca_marin_general_relief_liquid_asset_eligible", period
        )
        personal_property_eligible = spm_unit(
            "ca_marin_general_relief_personal_property_eligible", period
        )
        income_eligible = spm_unit("ca_marin_general_relief_income_eligible", period)
        # SSI/SSP recipients are categorically ineligible for General Relief.
        # `ssi > 0` already implies SSI receipt; the unit is barred if any
        # member receives SSI.
        receives_ssi = spm_unit.any(spm_unit.members("ssi", period) > 0)
        return (
            age_eligible
            & immigration_eligible
            & liquid_asset_eligible
            & personal_property_eligible
            & income_eligible
            & ~receives_ssi
        )
