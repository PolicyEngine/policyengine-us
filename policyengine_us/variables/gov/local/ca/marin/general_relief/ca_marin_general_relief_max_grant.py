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
        # The couple grant ($636) applies only when the unit is married AND both
        # applicants are immigration-eligible; otherwise the eligible applicant
        # is aided at the single rate ($387). The Standards do not address
        # mixed-status couples, so we assume the single rate (the ineligible
        # spouse's income is still counted via SPM-unit pooling). Counting how
        # many applicants qualify is why the per-person immigration variable
        # exists -- a unit-level boolean cannot give the ">= 2" count. Mirrors LA
        # County GR; in rare multi-adult units this gate may not verify the two
        # are married to each other.
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
