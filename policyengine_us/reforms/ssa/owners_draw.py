"""Optional SECA treatment of owners' signed pass-through residual profits.

The parallel draw base leaves the existing SE base available for cap ordering
and adds liability to the ordinary SECA tax leaves exactly once. See
docs/contributed_reforms/owners_draw.md for the input and classification contract.
"""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_social_security_tax import (
    self_employment_social_security_tax as baseline_oasdi_tax,
)
from policyengine_us.variables.gov.irs.tax.self_employment.self_employment_medicare_tax import (
    self_employment_medicare_tax as baseline_hi_tax,
)
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.self_employment_tax_ald_person import (
    self_employment_tax_ald_person as baseline_se_deduction,
)
from policyengine_us.variables.gov.ssa.social_security.ss_aime import (
    ss_aime as baseline_aime,
    _compute_aime,
)


def _enabled(period, parameters):
    p = parameters(period).gov.contrib.ssa.owners_draw
    return p.in_effect and period.start.year >= p.start_year


def _share(period, parameters):
    p = parameters(period).gov.contrib.ssa.owners_draw
    if not _enabled(period, parameters):
        return 0
    if p.phase_in_years < 1 or int(p.phase_in_years) != p.phase_in_years:
        raise ValueError("Owners' draw phase_in_years must be a positive integer")
    if p.phase_in_share == -1:
        return min(1, (period.start.year - p.start_year + 1) / p.phase_in_years)
    if not np.isfinite(p.phase_in_share) or not 0 <= p.phase_in_share <= 1:
        raise ValueError("Owners' draw phase_in_share must be -1 or in [0, 1]")
    return p.phase_in_share


def create_owners_draw():
    class owners_draw_subsets_are_disjoint(Variable):
        value_type = bool
        entity = Person
        definition_period = YEAR
        label = "Assert passive and already-SE pass-through subsets are disjoint"
        documentation = (
            "Caller-validated assertion for the supplied signed entity totals. "
            "Otherwise supply owners_draw_passive_se_overlap when both subsets "
            "are nonzero."
        )

    class owners_draw_passive_se_overlap(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        default_value = np.nan
        label = "Signed overlap of passive and already-SE partnership income"
        documentation = (
            "Intersection already included in both passive pass-through income "
            "and partnership SE net earnings, not an additional income source."
        )

    class owners_draw_active_income(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Signed pass-through residual eligible for owners' draw"
        reference = "https://www.ssa.gov/OACT/solvency/provisions/coverage.html"

        def formula(person, period, parameters):
            if not _enabled(period, parameters):
                return 0
            total = add(person, period, ["s_corp_income", "partnership_income"])
            already_se = person("partnership_self_employment_net_earnings", period)
            if not parameters(
                period
            ).gov.contrib.ssa.owners_draw.material_participation_only:
                return total - already_se
            passive = person("passive_partnership_s_corp_income", period)
            disjoint = person("owners_draw_subsets_are_disjoint", period)
            overlap = person("owners_draw_passive_se_overlap", period)
            unknown_overlap = ~np.isfinite(overlap)
            ambiguous = (passive != 0) & (already_se != 0) & ~disjoint & unknown_overlap
            if np.any(ambiguous):
                raise ValueError(
                    "Owners' draw needs a validated disjoint-subset assertion "
                    "or explicit passive/SE overlap when both subsets are nonzero"
                )
            if np.any(disjoint & ~unknown_overlap & (overlap != 0)):
                raise ValueError(
                    "Owners' draw disjoint assertion contradicts supplied overlap"
                )
            # Net signed entity profits/losses before flooring. The residual
            # does not offset wages or the preexisting SE earnings base.
            return total - passive - already_se + where(unknown_overlap, 0, overlap)

    class owners_draw_planned_gross(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Planned gross owners' draw before the separate reporting floor"

        def formula(person, period, parameters):
            return _share(period, parameters) * max_(
                0, person("owners_draw_active_income", period)
            )

    class owners_draw_net_earnings_factor(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "Net earnings factor applied to owners' draw"

        def formula(person, period, parameters):
            if not _enabled(period, parameters):
                return 0
            p = parameters(period).gov
            factor = p.contrib.ssa.owners_draw.net_earnings_factor
            if factor == 0:
                factor = 1 - p.irs.ald.misc.employer_share * (
                    p.irs.self_employment.rate.social_security
                    + p.irs.self_employment.rate.medicare
                )
            if not np.isfinite(factor) or not 0 < factor <= 1:
                raise ValueError("Owners' draw net earnings factor must be in (0, 1]")
            return factor

    class owners_draw_gross(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Actual gross owners' draw accepted by the reporting floor"

        def formula(person, period, parameters):
            planned = person("owners_draw_planned_gross", period)
            adjusted = planned * person("owners_draw_net_earnings_factor", period)
            floor = parameters(period).gov.irs.self_employment.net_earnings_exemption
            return where(adjusted >= floor, planned, 0)

    class owners_draw_net_earnings(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Adjusted owners' draw before the OASDI room cap"

        def formula(person, period, parameters):
            return person("owners_draw_gross", period) * person(
                "owners_draw_net_earnings_factor", period
            )

    class owners_draw_oasdi_room(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "OASDI room after wages and existing adjusted SE earnings"

        def formula(person, period, parameters):
            if not _enabled(period, parameters):
                return 0
            p = parameters(period).gov.contrib.ssa.owners_draw
            if p.room_cap_basis == 1:
                return np.inf
            if p.room_cap_basis != 0:
                raise ValueError(
                    "Owners' draw room_cap_basis must be 0 (current law) or 1 (no ceiling)"
                )
            wages = person("taxable_earnings_for_social_security", period)
            existing_se = person(
                "social_security_taxable_self_employment_income", period
            )
            # The existing base is already adjusted and capped; #10376 also
            # floors its room when another reform taxes above-cap wages.
            return max_(0, p.current_law_cap - wages - existing_se)

    class owners_draw_oasdi_base(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Owners' draw subject to SECA OASDI"

        def formula(person, period, parameters):
            return min_(
                person("owners_draw_net_earnings", period),
                person("owners_draw_oasdi_room", period),
            )

    class owners_draw_oasdi_tax(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Incremental SECA OASDI tax on owners' draw"

        def formula(person, period, parameters):
            rate = parameters(period).gov.irs.self_employment.rate.social_security
            return rate * person("owners_draw_oasdi_base", period)

    class owners_draw_hi_tax(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Optional incremental SECA HI tax on owners' draw"

        def formula(person, period, parameters):
            if not parameters(period).gov.contrib.ssa.owners_draw.include_hi:
                return 0
            rate = parameters(period).gov.irs.self_employment.rate.medicare
            return rate * person("owners_draw_net_earnings", period)

    class owners_draw_niit_exclusion(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Gross owners' profits subject to SECA for active NIIT exclusion"
        documentation = (
            "Subtract from a broadened active NIIT residual: OASDI base divided "
            "by the netting factor, or the whole actual gross draw with HI on. "
            "Existing gross active partnership SE earnings are excluded separately."
        )

        def formula(person, period, parameters):
            if not _enabled(period, parameters):
                return 0
            if parameters(period).gov.contrib.ssa.owners_draw.include_hi:
                return person("owners_draw_gross", period)
            return person("owners_draw_oasdi_base", period) / person(
                "owners_draw_net_earnings_factor", period
            )

    class owners_draw_credited_earnings(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Adjusted owners' draw available to an annual benefit ledger"
        documentation = (
            "Add to annual covered earnings before the ordinary benefit cap. "
            "This flag has no effect on tax liability or reported benefits."
        )

        def formula(person, period, parameters):
            if not parameters(period).gov.contrib.ssa.owners_draw.benefit_credit:
                return 0
            return person("owners_draw_net_earnings", period)

    class self_employment_social_security_tax(baseline_oasdi_tax):
        def formula(person, period, parameters):
            return baseline_oasdi_tax.formula(person, period, parameters) + person(
                "owners_draw_oasdi_tax", period
            )

    class self_employment_medicare_tax(baseline_hi_tax):
        def formula(person, period, parameters):
            return baseline_hi_tax.formula(person, period, parameters) + person(
                "owners_draw_hi_tax", period
            )

    class self_employment_tax_ald_person(baseline_se_deduction):
        def formula(person, period, parameters):
            if not _enabled(period, parameters):
                return baseline_se_deduction.formula(person, period, parameters)
            p = parameters(period).gov
            deductible_tax = person("self_employment_tax", period)
            if not p.contrib.ssa.owners_draw.half_seca_deduction:
                deductible_tax = max_(
                    0,
                    deductible_tax
                    - add(
                        person, period, ["owners_draw_oasdi_tax", "owners_draw_hi_tax"]
                    ),
                )
            return deductible_tax * p.irs.ald.self_employment_tax.percent_deductible

    class ss_aime(baseline_aime):
        def formula(person, period, parameters):
            supplied = person("ss_aime_input", period)
            computed = _compute_aime(
                person,
                period,
                parameters,
                additional_earnings_variable="owners_draw_credited_earnings",
            )
            return where(supplied > 0, supplied, computed)

    class reform(Reform):
        def apply(self):
            for variable in (
                owners_draw_subsets_are_disjoint,
                owners_draw_passive_se_overlap,
                owners_draw_active_income,
                owners_draw_planned_gross,
                owners_draw_net_earnings_factor,
                owners_draw_gross,
                owners_draw_net_earnings,
                owners_draw_oasdi_room,
                owners_draw_oasdi_base,
                owners_draw_oasdi_tax,
                owners_draw_hi_tax,
                owners_draw_niit_exclusion,
                owners_draw_credited_earnings,
            ):
                self.update_variable(variable)
            self.update_variable(self_employment_social_security_tax)
            self.update_variable(self_employment_medicare_tax)
            self.update_variable(self_employment_tax_ald_person)
            self.update_variable(ss_aime)

    return reform


def create_owners_draw_reform(parameters, period, bypass=False):
    if bypass or any(
        value.value
        for value in parameters.gov.contrib.ssa.owners_draw.in_effect.values_list
    ):
        return create_owners_draw()
    return None


owners_draw = create_owners_draw_reform(None, None, bypass=True)
