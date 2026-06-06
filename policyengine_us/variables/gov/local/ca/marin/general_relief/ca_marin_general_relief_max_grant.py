from policyengine_us.model_api import *


class ca_marin_general_relief_max_grant(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Maximum Marin County General Relief cash aid amount"
    definition_period = MONTH
    defined_for = "in_marin"
    reference = "https://marin.granicus.com/DocumentViewer.php?file=marin_ce4ed1aaf509aaf7176c360d26f8f1c6.pdf#page=17"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.marin.general_relief
        # spm_unit_is_married is a YEAR-defined boolean, so read it with
        # period.this_year from this MONTH formula to avoid period conversion.
        married = spm_unit("spm_unit_is_married", period.this_year)
        # The couple grant applies only when both members are immigration
        # eligible; otherwise the unit receives the single grant. Mirrors LA
        # County GR. This assumes the SPM unit is a married couple (both members
        # immigration-eligible); in rare multi-adult units this gate may not
        # verify the two are married to each other.
        immigration_eligible_count = add(
            spm_unit,
            period,
            ["ca_marin_general_relief_immigration_status_eligible_person"],
        )
        return where(
            married & (immigration_eligible_count >= 2),
            p.amount.married,
            p.amount.single,
        )
