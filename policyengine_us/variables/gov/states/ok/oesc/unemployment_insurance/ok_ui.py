from policyengine_us.model_api import *


class ok_ui(Variable):
    """Annual Oklahoma Unemployment Insurance benefit. Implements the
    monetary eligibility tests (§ 2-207), weekly benefit rate (§ 2-104),
    partial benefit subtraction (§ 2-105), and benefit duration cap
    (§ 2-106 / § 1-231).

    Not modeled: § 1-202.1 / § 1-202.2 alternative and extended base
    periods; § 2-104(B) max-WBA percentage derivation by fund condition
    (only the resulting maximum dollar amount is parameterized); § 1-231(A)
    claim-volume duration escalation to 20 or 26 weeks; § 2-107 portion-
    of-a-week proration; § 2-108 approved training waiver; § 2-202 /
    § 2-205.1 able-available-seeking-work; § 2-206 one-week waiting period;
    § 2-208 alien-status rules; § 2-109 10x WBA requalification; all
    § 2-404 through § 2-422 disqualifications.
    """

    value_type = float
    entity = Person
    label = "Oklahoma unemployment insurance"
    unit = USD
    definition_period = YEAR
    defined_for = "ok_ui_monetarily_eligible"
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=50",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=51",
    )

    def formula(person, period, parameters):
        weekly_payable = person("ok_ui_weekly_payable", period)
        maximum_benefit_amount = person("ok_ui_maximum_benefit_amount", period)
        weeks_unemployed = person("weeks_unemployed", period)
        annual_benefit = weekly_payable * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
