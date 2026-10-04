from policyengine_us.model_api import *


class wv_lieap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia LIEAP annual countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/39948/download?inline=#page=1725,1726,1727,1728",
        "https://bfa.wv.gov/media/40005/download?inline=#page=1726,1727,1728,1729",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.lieap.income
        person = spm_unit.members
        # Existing net business inputs receive no second expense deduction;
        # business and estate losses do not offset other income.
        net_income = sum(
            max_(person(source, period), 0) for source in p.nonnegative_sources
        )
        # The operative manual counts minor and nonqualified members' income,
        # TANF and general assistance. RSDI and SSI are expressly excluded.
        # Annual flows approximate recurring application-month receipts. Generic
        # VA cannot identify excluded Aid and Attendance; see README limitations.
        return max_(spm_unit.sum(net_income) + add(spm_unit, period, p.sources), 0)
