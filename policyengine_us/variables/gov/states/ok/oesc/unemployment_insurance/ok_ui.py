from policyengine_us.model_api import *


class ok_ui(Variable):
    """Annual Oklahoma Unemployment Insurance benefit. Implements the
    monetary eligibility tests (§ 2-207), weekly benefit rate (§ 2-104),
    partial benefit subtraction (§ 2-105), and benefit duration cap
    (§ 2-106 / § 1-231).

    Not modeled: § 1-202.1 alternative and extended base periods; § 2-104(B)
    max-WBA percentage derivation by fund condition (only the resulting
    maximum dollar amount is parameterized); § 2-106(2) statutory
    %-of-average-annual-wage benefit-year cap (OESC-published proxy used
    instead); § 1-217(B)(2) 15% wage/hour-loss unemployment prong; § 1-231
    16-to-26-week claim-volume duration escalation above the 16-week floor;
    § 2-107 portion-of-a-week proration; § 2-108 approved training waiver;
    § 2-202 / § 2-205.1 able-available-seeking-work; § 2-206 one-week waiting
    period; § 2-208 alien-status rules; § 2-109 10x WBA requalification; all
    § 2-404 through § 2-422 disqualifications.
    """

    value_type = float
    entity = Person
    label = "Oklahoma unemployment insurance"
    documentation = (
        "Annual Oklahoma Unemployment Insurance benefit. Not modeled: the "
        "§ 2-106(2) statutory percentage-of-average-annual-wage benefit-year "
        "cap (an OESC-published proxy is used); the § 1-231 claim-volume "
        "duration escalation above the 16-week floor (up to 20 or 26 weeks); "
        "the § 1-217(B)(2) 15% wage/hour-loss partial-unemployment prong; the "
        "§ 2-206 one-week waiting period; the § 1-202.1 alternative and "
        "extended base periods; and the § 2-404 through "
        "§ 2-422 nonmonetary disqualifications, waiting week, and "
        "able-available-seeking-work requirements."
    )
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
        # Guard against negative weeks so the benefit cannot go below zero.
        weeks_unemployed = max_(person("weeks_unemployed", period), 0)
        annual_benefit = weekly_payable * weeks_unemployed
        return min_(annual_benefit, maximum_benefit_amount)
