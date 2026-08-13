from policyengine_us.model_api import *


class il_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Illinois CCAP monthly family copayment"
    defined_for = StateCode.IL
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=54862",
        "https://www.dhs.state.il.us/OneNetLibrary/27897/documents/Forms/443455B%20CCAP%20Income%20and%20Copay%20Chart%20Eff%207.1.25.pdf#page=2",
        "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-3455B%20DEC%20-%20Important%20Parent%20Co-Payment%20Information%207.1.26.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        income = spm_unit("il_ccap_countable_income", period)
        family_size = clip(
            spm_unit("spm_unit_size", period.this_year),
            p.copay.family_size.minimum,
            p.copay.family_size.maximum,
        ).astype(int)

        table_a_copay = np.zeros_like(income)
        for size in range(
            int(p.copay.family_size.minimum),
            int(p.copay.family_size.maximum) + 1,
        ):
            scale = getattr(p.copay.table_a, f"family_size_{size}")
            table_a_copay = where(
                family_size == size,
                scale.calc(income),
                table_a_copay,
            )

        fpg = spm_unit("spm_unit_fpg", period)
        ordinary_copay = where(
            income <= fpg * p.copay.fpl_reduced_rate,
            p.copay.fpl_minimum_amount,
            table_a_copay,
        )
        # We do not model the Table B school-age part-day copayment schedule.
        zero_copay = spm_unit(
            "il_ccap_non_parent_relative_child_only_tanf",
            period,
        ) | spm_unit("il_ccap_protective_care_copay_exempt", period)
        # We do not model the $1 child care worker copayment.
        assessed_copay = where(zero_copay, 0, ordinary_copay)
        return where(p.in_effect, assessed_copay, 0)
