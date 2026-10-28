from policyengine_us.model_api import *
from policyengine_us.reforms.congress.s770.section_8 import active_residual


class s770_active_business_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "S.770 signed active business income outside FICA and SECA"
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
    documentation = (
        "Signed head/spouse pass-through residual: partnership_s_corp_income "
        "(s_corp_income + partnership_income), less its passive subset, "
        "already-SE active subset, and amounts actually subject to FICA/SECA "
        "under the owners-draw integration hooks. Passive and already-SE "
        "subsets must be disjoint unless s770_passive_se_income supplies their "
        "intersection. Nonpassive status is only a material-participation "
        "proxy; entity-level netting and legal limited-partner classifications "
        "are not identified. Certified unrepaired data have zero S-corp income, "
        "combined partnership income carrying passive mass, and no passive "
        "subset: this overstates the active base and understates NII until "
        "Microcosm #1251/#1261 repairs appear in the scoring artifact."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.irs
        q = 1 - p.ald.misc.employer_share * (
            p.self_employment.rate.social_security + p.self_employment.rate.medicare
        )
        if q <= 0:
            raise ValueError("S.770 owners-draw netting factor must be positive")
        # M7: OASDI-only draws exclude only profits actually taxed after cap
        # room. Uncapped HI draws exclude all actual gross draw, never planned D.
        draw_exclusion = where(
            person("s770_draw_hi_in_effect", period),
            person("s770_draw_gross", period),
            person("s770_draw_oasdi_base", period) / q,
        )
        active_se = person("partnership_self_employment_net_earnings", period) - person(
            "s770_passive_se_income", period
        )
        residual = active_residual(
            person("partnership_s_corp_income", period),
            person("passive_partnership_s_corp_income", period),
            active_se,
            draw_exclusion + person("s770_active_fica_income", period),
        )
        return tax_unit.sum(~person("is_tax_unit_dependent", period) * residual)
