from policyengine_us.model_api import *


class snap_expense_counted_share(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP share of expenses counted toward deductions"
    definition_period = MONTH
    unit = "/1"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2_iii",
        "https://www.law.cornell.edu/cfr/text/7/273.11#d_1",
    )

    def formula(spm_unit, period, parameters):
        # Shared expenses are assumed to be paid evenly per capita, and
        # each payer's per capita portion counts at that member's income
        # counted share: ineligible students are nonhousehold members
        # whose payments are not the household's expense (273.11(d)(1));
        # the portion paid by prorated members is divided evenly among
        # household members with all but the ineligible members' shares
        # counted (273.11(c)(2)(iii)); and expenses of members sanctioned
        # under 273.11(c)(1) continue to count in their entirety.
        person = spm_unit.members
        share = person("snap_income_counted_share", period)
        size = spm_unit("spm_unit_size", period.this_year)
        # Subtract the uncounted portion of each member's per capita
        # payment rather than summing counted shares directly, so a
        # spm_unit_size exceeding the modeled member count leaves the
        # share at one.
        return max_(1 - spm_unit.sum(1 - share) / max_(size, 1), 0)
