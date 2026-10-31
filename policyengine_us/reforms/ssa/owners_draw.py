"""Optional SECA treatment of owners' signed pass-through residual profits.

The parallel draw base leaves the existing SE base available for cap ordering
and adds liability to the ordinary SECA tax leaves exactly once. See
docs/contributed_reforms/owners_draw.md for the input and classification contract.
"""

from policyengine_us.model_api import *
from policyengine_us.tools.social_security.owners_draw import (
    OwnersDrawParameters,
    compute_owners_draw,
)
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


_DRAW_INPUT_VARIABLES = {
    "s_corp_income": "s_corp_income",
    "partnership_income": "partnership_income",
    "passive_income": "passive_partnership_s_corp_income",
    "already_se_income": "partnership_self_employment_net_earnings",
    "subsets_are_disjoint": "owners_draw_subsets_are_disjoint",
    "passive_se_overlap": "owners_draw_passive_se_overlap",
    "covered_wages": "taxable_earnings_for_social_security",
    "existing_covered_se": "social_security_taxable_self_employment_income",
}


def _draw(person, period, parameters, output):
    """Delegate one stage while honoring directly supplied intermediate inputs."""
    return compute_owners_draw(
        period.start.year,
        inputs=lambda name: person(_DRAW_INPUT_VARIABLES[name], period),
        parameters=OwnersDrawParameters.from_policy_parameters(
            parameters(period).gov, year=period.start.year, output=output
        ),
        output=output,
        overrides=lambda name: person(f"owners_draw_{name}", period),
    )


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
            return _draw(person, period, parameters, "active_income")

    class owners_draw_planned_gross(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Planned gross owners' draw before the separate reporting floor"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "planned_gross")

    class owners_draw_net_earnings_factor(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "Net earnings factor applied to owners' draw"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "net_earnings_factor")

    class owners_draw_gross(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Actual gross owners' draw accepted by the reporting floor"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "gross")

    class owners_draw_net_earnings(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Adjusted owners' draw before the OASDI room cap"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "net_earnings")

    class owners_draw_oasdi_room(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "OASDI room after wages and existing adjusted SE earnings"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "oasdi_room")

    class owners_draw_oasdi_base(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Owners' draw subject to SECA OASDI"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "oasdi_base")

    class owners_draw_oasdi_tax(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Incremental SECA OASDI tax on owners' draw"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "oasdi_tax")

    class owners_draw_hi_tax(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        unit = USD
        label = "Optional incremental SECA HI tax on owners' draw"

        def formula(person, period, parameters):
            return _draw(person, period, parameters, "hi_tax")

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
            return _draw(person, period, parameters, "niit_exclusion")

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
            return _draw(person, period, parameters, "credited_earnings")

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
