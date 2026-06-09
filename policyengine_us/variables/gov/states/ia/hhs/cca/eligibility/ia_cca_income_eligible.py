from policyengine_us.model_api import *


class ia_cca_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Iowa CCA based on income"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.income.fpl_rate
        countable_income = spm_unit("ia_cca_countable_income", period)
        # spm_unit_fpg is YEAR-defined; the bare monthly period auto-divides
        # it to a monthly poverty guideline, matching the monthly income.
        fpg = spm_unit("spm_unit_fpg", period)
        enrolled = spm_unit("ia_cca_enrolled", period)
        # The family standard rises if any eligible child receives
        # special-needs care.
        has_special_needs_child = spm_unit("ia_cca_has_special_needs_child", period)

        initial_fpl_rate = where(
            has_special_needs_child,
            p.initial_special_needs,
            p.initial_basic,
        )
        # Already-enrolled families stay eligible up to the higher ongoing
        # CCA Exit limit (250% basic / 275% special-needs FPL).
        exit_fpl_rate = where(
            has_special_needs_child,
            p.exit_special_needs,
            p.exit_basic,
        )
        initial_limit = min_(fpg * initial_fpl_rate, spm_unit("ia_cca_smi", period))
        exit_limit = fpg * exit_fpl_rate
        # IAC 441-170.2(1)"a" sets three income tiers: initial (a(1),
        # min of 160%/200% FPL and 85% MFI), ongoing CCA Plus (a(2),
        # min of 225% FPL and 85% MFI), and ongoing CCA Exit (a(3),
        # 250%/275% FPL with no MFI cap). We collapse the two ongoing tiers
        # into the higher CCA Exit ceiling for enrolled families, so the a(2)
        # 225%-FPL-with-85%-MFI-cap intermediate ceiling is not represented.
        # The 85% MFI cap is correctly absent from a(3). The omitted a(2) cap
        # only binds below the 225% FPL standard at very large family sizes
        # (where 85% MFI falls below 225% FPL), and the model uses the 225%
        # FPL standard solely as the copay-mechanism dispatch boundary
        # (CCA/CCA Plus sliding fee vs. CCA Exit percentage), never as an
        # income-eligibility ceiling, so this simplification is immaterial.
        income_limit = where(enrolled, exit_limit, initial_limit)
        return countable_income <= income_limit
