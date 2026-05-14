from policyengine_us.model_api import *


class ga_qualified_overtime_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia qualified overtime compensation exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080",  # GA HB463 Section 2-4 adding O.C.G.A. 48-7-27(a)(16)
    )

    def formula(tax_unit, period, parameters):
        # GA HB463 Section 2-4 paragraph (16): for tax years 2026-2028, each
        # full-time hourly employee may exclude up to $1,750 of qualified
        # overtime compensation (IRC section 225) from Georgia taxable income.
        # We approximate the "full-time employee paid by an hourly wage"
        # restriction by using fsla_overtime_premium, which is the federally-
        # defined Fair Labor Standards Act overtime premium and by definition
        # applies only to non-exempt (typically hourly) workers.
        person = tax_unit.members
        overtime = person("fsla_overtime_premium", period)
        cap = parameters(period).gov.states.ga.tax.income.agi.exclusions.overtime.cap
        capped = min_(overtime, cap)
        return tax_unit.sum(capped)
