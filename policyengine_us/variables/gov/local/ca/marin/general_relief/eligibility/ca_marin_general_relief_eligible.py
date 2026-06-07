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
        age_eligible = spm_unit("ca_marin_general_relief_age_eligible", period)
        # At least one applicant (head/spouse) must hold a qualifying immigration
        # status. The person-level check is its own variable because it also
        # feeds the couple-grant count in max_grant; here we just aggregate it.
        immigration_eligible = spm_unit.any(
            spm_unit.members(
                "ca_marin_general_relief_immigration_status_eligible_person", period
            )
        )
        liquid_asset_eligible = spm_unit(
            "ca_marin_general_relief_liquid_asset_eligible", period
        )
        personal_property_eligible = spm_unit(
            "ca_marin_general_relief_personal_property_eligible", period
        )
        income_eligible = spm_unit("ca_marin_general_relief_income_eligible", period)
        # Marin GR is limited to adults with no dependent children (or <50%
        # custody) per Marin HHS, so any unit containing a dependent child is
        # excluded. A dependent child is a tax-unit dependent under 18;
        # tax-dependency approximates the >=50% custody rule -- a child claimed
        # here is the applicant's responsibility, while a <50%-custody child
        # claimed elsewhere does not trigger the gate. This explicit gate also
        # excludes dependent families that CalWORKs misses for non-income
        # reasons (e.g. a vehicle over the CalWORKs limit).
        person = spm_unit.members
        is_dependent_child = person("is_tax_unit_dependent", period.this_year) & person(
            "is_child", period.this_year
        )
        has_dependent_child = spm_unit.any(is_dependent_child)
        # SSI/SSP recipients are categorically ineligible for General Relief.
        # `ssi > 0` already implies SSI receipt; the unit is barred if any member
        # receives SSI. CAPI (California's SSI-equivalent cash for immigrants)
        # needs no separate bar: CAPI recipients are non-qualified noncitizens
        # who fail the immigration check above.
        receives_ssi = spm_unit.any(spm_unit.members("ssi", period) > 0)
        return (
            age_eligible
            & immigration_eligible
            & liquid_asset_eligible
            & personal_property_eligible
            & income_eligible
            & ~has_dependent_child
            & ~receives_ssi
        )
