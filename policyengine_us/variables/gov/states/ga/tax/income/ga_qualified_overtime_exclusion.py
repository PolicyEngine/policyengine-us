from policyengine_us.model_api import *


class ga_qualified_overtime_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia qualified overtime compensation exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    # GA HB463 Section 2-4 adds O.C.G.A. § 48-7-27(a)(16).
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080#page=6",
        "https://dor.georgia.gov/document/document/2026-employers-tax-guide-updated-june-2026/download#page=4",
    )

    def formula(tax_unit, period, parameters):
        # O.C.G.A. § 48-7-27(a)(16) (TY 2026-2028): two amounts count toward
        # one $1,750 limit per full-time employee.
        #   - (16)(A): qualified overtime compensation, defined by reference
        #     to IRC § 225, "received by a full-time employee paid by an hourly
        #     wage". `fsla_overtime_premium` holds the § 225 amount, and it
        #     counts only for a person paid hourly. Reading
        #     `is_eligible_for_fsla_overtime` as well would add nothing: it is
        #     always true for a person paid hourly.
        #   - (16)(B): "notwithstanding subparagraph (A)", for employers
        #     governed by the federal Railway Labor Act, "the exemption
        #     provided in this paragraph" applies to hourly component overtime
        #     compensation as collective bargaining agreements define it. That
        #     class takes the place of the § 225 amount and of the hourly wage
        #     test, since pay with an hourly component need not be an hourly
        #     wage. (B) leaves the limit and full-time status alone, so both
        #     stay, and the DOR's guide keeps the limit. 29 U.S.C. § 213(b)(2)-
        #     (3) takes rail and air carrier employees out of FLSA overtime,
        #     so this pay is a separate input.
        #
        # The employer reporting rules in (16)(C)-(D) do not affect liability.
        #
        # § 48-7-27(a) subtracts the exclusion from the taxpayer's federal
        # adjusted gross income. A dependent's overtime is the dependent's own
        # income (26 U.S.C. 73(a) for a child's services), left out of the
        # filer's federal AGI (see irs_gross_income), so it never counts.
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions.overtime
        hourly = person("is_paid_hourly", period)
        full_time = person("ga_qualified_overtime_full_time_employee", period)
        qualified_overtime = person("fsla_overtime_premium", period) * hourly
        rla_overtime = person("ga_rla_hourly_component_overtime", period)
        overtime = (qualified_overtime + rla_overtime) * full_time
        not_dependent = ~person("is_tax_unit_dependent", period)
        return tax_unit.sum(min_(overtime, p.cap) * not_dependent)
