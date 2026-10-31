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
        # O.C.G.A. § 48-7-27(a)(16) (TY 2026-2028) excludes up to $1,750 per
        # employee, for "a full-time employee paid by an hourly wage". Two
        # amounts count toward that one limit:
        #   - (16)(A): qualified overtime compensation, defined by reference
        #     to IRC § 225, which `fsla_overtime_premium` holds. Reading
        #     `is_eligible_for_fsla_overtime` as well would add nothing: the
        #     variable is true whenever `is_paid_hourly` is.
        #   - (16)(B): "notwithstanding subparagraph (A)", for employers
        #     governed by the federal Railway Labor Act, "the exemption
        #     provided in this paragraph" applies to hourly component overtime
        #     compensation as collective bargaining agreements define it. That
        #     class replaces the § 225 amount, which 29 U.S.C. § 213(b)(2)-(3)
        #     puts out of reach for rail and air carrier employees. (B) changes
        #     nothing else in (A), so the limit and both employee tests stay.
        #     It has no years of its own, so it relies on (A).
        #
        # The employer reporting rules in (16)(C)-(D) do not affect liability.
        #
        # § 48-7-27(a) subtracts the exclusion from the taxpayer's federal
        # adjusted gross income. A dependent's overtime is the dependent's own
        # income (26 U.S.C. 73(a) for a child's services), left out of the
        # filer's federal AGI (see irs_gross_income), so it never counts.
        person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.agi.exclusions.overtime
        overtime = add(
            person,
            period,
            ["fsla_overtime_premium", "ga_rla_hourly_component_overtime"],
        )
        eligible = person("is_paid_hourly", period) & person(
            "ga_qualified_overtime_full_time_employee", period
        )
        not_dependent = ~person("is_tax_unit_dependent", period)
        return tax_unit.sum(min_(overtime * eligible, p.cap) * not_dependent)
