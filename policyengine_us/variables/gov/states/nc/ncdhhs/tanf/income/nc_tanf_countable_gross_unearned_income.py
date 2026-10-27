from policyengine_us.model_api import *


class nc_tanf_countable_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = (
        "https://www.ncdhhs.gov/efs-wf-06-2025a2/open#page=18",
        "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=2",
        "http://reports.oah.state.nc.us/ncac/title%2010a%20-%20health%20and%20human%20services/chapter%2071%20-%20adult%20and%20family%20support/subchapter%20w/subchapter%20w%20rules.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf.income
        person = spm_unit.members
        # State Plan Financial Rules 3 and 4: no income of SSI recipients
        # is counted.
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        # Sum unearned sources, plus child support if not currently enrolled.
        gross_unearned = add(person, period, p.unearned)
        child_support = person("child_support_received", period)
        countable_unearned = spm_unit.sum(where(is_ssi_recipient, 0, gross_unearned))
        countable_child_support = spm_unit.sum(
            where(is_ssi_recipient, 0, child_support)
        )
        tanf_enrolled = spm_unit("is_tanf_enrolled", period.first_month)
        additional_amount = where(tanf_enrolled, 0, countable_child_support)
        return countable_unearned + additional_amount
