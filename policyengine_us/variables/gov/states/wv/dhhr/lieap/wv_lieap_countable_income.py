from policyengine_us.model_api import *


class wv_lieap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia LIEAP annual countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    reference = (
        # PDF pages 1732-1735
        "https://web.archive.org/web/20260302130424/https://bfa.wv.gov/media/39948/download?inline#page=1732",
        # PDF pages 1726-1729
        "https://web.archive.org/web/20261023203756/https://bfa.wv.gov/media/40005/download?inline#page=1726",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.lieap.income
        person = spm_unit.members
        # Floor each member/source before aggregation so losses cannot erase
        # another receipt. The operative manual counts minor and nonqualified members' income,
        # TANF and general assistance. RSDI and SSI are expressly excluded.
        # Annual flows approximate recurring application-month receipts. Generic
        # VA cannot identify excluded Aid and Attendance.
        income = 0
        for source in p.sources:
            income = income + max_(add(person, period, [source]), 0)
        return spm_unit.sum(income) + spm_unit("tanf", period)
