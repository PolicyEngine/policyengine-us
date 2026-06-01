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
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080#page=6"
    )

    def formula(tax_unit, period, parameters):
        # GA HB463 § 48-7-27(a)(16) (TY 2026-2028): each full-time hourly
        # employee may exclude up to $1,750 of qualified overtime compensation
        # (defined by reference to IRC § 225) from Georgia taxable income.
        #
        # Approximation: we use `fsla_overtime_premium`, the federally-defined
        # Fair Labor Standards Act overtime premium, which by construction
        # applies only to FLSA non-exempt workers (typically hourly). Known
        # limitations:
        #   - The bill's "full-time" qualifier is not strictly enforced;
        #     a part-time hourly worker who happens to exceed 40 hours in
        #     some weeks would be credited the exclusion under the model.
        #   - § 48-7-27(a)(16)(B) extends the exclusion to railway workers
        #     under the National Railway Labor Act, defined by collective
        #     bargaining agreements. Railway workers are FLSA-exempt under
        #     29 U.S.C. § 213(b)(2), so `fsla_overtime_premium` returns zero
        #     for them and they receive no exclusion under the model. This
        #     is a known under-modeling of a specifically eligible group.
        #   - The employer reporting obligations in § 48-7-27(a)(16)(C)-(D)
        #     are administrative and do not affect household tax liability.
        person = tax_unit.members
        overtime = person("fsla_overtime_premium", period)
        cap = parameters(period).gov.states.ga.tax.income.agi.exclusions.overtime.cap
        return tax_unit.sum(min_(overtime, cap))
