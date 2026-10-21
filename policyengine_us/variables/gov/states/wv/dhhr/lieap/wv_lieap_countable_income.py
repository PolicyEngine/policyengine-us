from policyengine_us.model_api import *


class wv_lieap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia LIEAP annual countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        # PDF pages 1725-1728
        "https://bfa.wv.gov/media/39948/download?inline=#page=1725",
        # PDF pages 1726-1729
        "https://bfa.wv.gov/media/40005/download?inline=#page=1726",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.lieap.income
        person = spm_unit.members
        # Existing net business inputs receive no second expense deduction;
        # business and estate losses do not offset other income.
        net_income = sum(
            max_(add(person, period, [source]), 0) for source in p.nonnegative_sources
        )
        # Floor each member/source before aggregation so losses cannot erase
        # another receipt. The operative manual counts minor and nonqualified members' income,
        # TANF and general assistance. RSDI and SSI are expressly excluded.
        # Annual flows approximate recurring application-month receipts. Generic
        # VA cannot identify excluded Aid and Attendance; see README limitations.
        receipts = sum(max_(add(person, period, [source]), 0) for source in p.sources)
        return spm_unit.sum(net_income + receipts) + max_(spm_unit("tanf", period), 0)
