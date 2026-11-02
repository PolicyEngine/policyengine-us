from policyengine_us.model_api import *


class wi_wheap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Wisconsin WHEAP categorical eligibility"
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/16/i/27",
        # Section 3.3.1 item 2, including item 2(d).
        # PDF pages 45-46
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=45",
        "https://liheapch.acf.gov/docs/2026/state-plans/WI_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        # Every member, including ineligible non-citizens, must receive W-2
        # cash, FoodShare or SSI. FoodShare covers only members of the SNAP
        # unit, and W-2 only citizens and qualified non-citizens. Unit-level
        # receipt approximates each member's group membership, and receipt in
        # any month approximates receipt for the entire prior month.
        person = spm_unit.members
        # Monthly flags are read month by month rather than as an annual
        # aggregate, which would cache a summed value under the annual key
        # and change what other formulas read.
        first_month = period.first_month
        months = [first_month.offset(offset) for offset in range(MONTHS_IN_YEAR)]
        reported_ssi = np.any(
            [person("receives_ssi", month) for month in months], axis=0
        )
        receives_ssi = (add(person, period, ["ssi"]) > 0) | reported_ssi
        in_snap_unit = np.any(
            [~person("is_snap_excluded_member", month) for month in months],
            axis=0,
        )
        receives_snap = spm_unit("snap", period, options=[ADD]) > 0
        foodshare_member = in_snap_unit & spm_unit.project(receives_snap)
        receives_w2_cash = spm_unit("tanf", period) > 0
        w2_member = person("is_citizen_or_legal_immigrant", period) & spm_unit.project(
            receives_w2_cash
        )
        return spm_unit.all(receives_ssi | foodshare_member | w2_member)
