"""Explicit, serializable selection of the canonical SPM forecast.

The calculator owns measurement formulas. The country owns model construction,
input handling and policy resources. Geography is never inferred from a missing
county: callers must explicitly select national or a particular metropolitan area.
"""

import re
from collections.abc import Mapping
from copy import copy, deepcopy
from functools import lru_cache
from inspect import signature

from policyengine_core.simulations import Simulation as CoreSimulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from spm_calculator.errors import SPMInputError
from spm_calculator.policyengine_adapter import (
    FORMULA_OWNED_INPUTS,
    PolicyEngineSPMProvider,
)
from spm_calculator.rolling_forecast import load_forecast


CONFIG_FIELDS = frozenset(
    {
        "forecast_content_sha256",
        "scenario",
        "geography_kind",
        "geography_id",
        "county_vintage",
        "as_of",
    }
)

COUNTY_FIPS_PATTERN = re.compile(r"[0-9]{5}")

COUNTY_INPUT_FIX = (
    'send county_fips as a five-digit string (for example "06037"), or select '
    'geography_kind="national" in the spm configuration'
)


def is_county_fips(value):
    """Accept only a five-digit county FIPS code.

    Integers, pandas missing values and truncated codes all arrive here as
    strings, because ``county_fips`` is a string variable and the model casts
    every input to its own dtype. A within-state CPS code such as ``5`` and a
    missing value such as ``nan`` are not county FIPS codes, so they must fail
    as an absent county rather than as an unrecognised one.
    """
    if value is None:
        return False
    if isinstance(value, bytes):
        value = value.decode()
    return COUNTY_FIPS_PATTERN.fullmatch(str(value)) is not None


class CountyRequiringSPMProvider(PolicyEngineSPMProvider):
    """Name the caller's fix when a county selection has no usable county.

    The calculator reports an absent county only for ``None`` and the empty
    string, and reports anything else as an unavailable county. A legacy
    population file storing the CPS within-state integer code, or a household
    request sending an integer or a missing value, would otherwise be told its
    county assignment is unavailable, which points at the artifact instead of
    at the input.
    """

    def calculate_unit(self, *, year, adults, children, tenure, county_fips=None):
        if self.geography_kind == "county" and not is_county_fips(county_fips):
            raise SPMInputError(
                "SPM_GEOGRAPHY_REQUIRED",
                f"County selection has no county FIPS input ({county_fips!r}): "
                f"{COUNTY_INPUT_FIX}",
            )
        return super().calculate_unit(
            year=year,
            adults=adults,
            children=children,
            tenure=tenure,
            county_fips=county_fips,
        )


def masked_policyengine_amount(unit, period, field, mask):
    """Return canonical float64 amounts for the units selected by ``mask``.

    The calculator's ``policyengine_amount`` evaluates every unit in the
    population, so a resource formula that only needs the SPM housing portion
    for units with housing assistance to cap would otherwise demand SPM
    geography and composition from units that never use them. Evaluate the
    selected units only, through the same provider path, so the county and
    composition requirements, the typed errors and the receipts attach to
    exactly the units whose result depends on the measurement. Unselected
    units return 0.0 and record nothing.
    """
    import numpy as np

    fields = (
        "reference_threshold",
        "unadjusted_threshold",
        "geographic_factor",
        "threshold",
        "housing_portion",
    )
    if field not in fields:
        raise ValueError(f"Unknown SPM amount field: {field}")
    index = fields.index(field)
    mask = np.asarray(mask, dtype=bool)
    result = np.zeros(mask.shape, dtype=np.float64)
    if not mask.any():
        return result
    bound = unit.simulation.tax_benefit_system.spm_forecast_provider
    adults = np.asarray(unit("spm_measurement_adults", period))[mask]
    children = np.asarray(unit("spm_measurement_children", period))[mask]
    if np.any(adults < 1):
        raise SPMInputError(
            "SPM_COMPOSITION_REQUIRED",
            "SPM unit has no classified adult: supply source-backed independence or household head/spouse structure",
        )
    tenures = np.asarray(unit("spm_unit_tenure_type", period).decode_to_str())[mask]
    if bound.geography_kind == "county":
        counties = np.asarray(unit.household("county_fips", period))[mask]
    else:
        counties = [None] * len(adults)
    rows = [
        bound._amounts(
            int(period.start.year),
            int(a),
            int(k),
            str(t).lower(),
            None if c is None else (c.decode() if isinstance(c, bytes) else str(c)),
        )
        for a, k, t, c in zip(adults, children, tenures, counties)
    ]
    result[mask] = [row[index] for row in rows]
    return result


@lru_cache(maxsize=1)
def _installed_forecast():
    """Verify the bundled immutable artifact once; never download data."""
    return load_forecast()


def create_spm_provider(config=None):
    """Resolve a public configuration against this installed calculator."""
    if config is None:
        config = {}
    if not isinstance(config, Mapping):
        raise TypeError("spm must be a mapping of explicit forecast settings")
    unknown = set(config) - CONFIG_FIELDS
    if unknown:
        raise ValueError(f"Unknown spm settings: {', '.join(sorted(unknown))}")
    forecast = _installed_forecast()
    expected = config.get("forecast_content_sha256")
    if expected is not None and expected != forecast.content_sha256:
        raise ValueError(
            "The installed SPM forecast does not match forecast_content_sha256"
        )
    return CountyRequiringSPMProvider(
        forecast=forecast,
        **{
            key: value
            for key, value in config.items()
            if key != "forecast_content_sha256"
        },
    )


def spm_config(provider):
    """Return detached JSON-compatible settings suitable for a bundle receipt."""
    return {
        "forecast_content_sha256": provider.forecast.content_sha256,
        "scenario": provider.scenario,
        "geography_kind": provider.geography_kind,
        "geography_id": provider.geography_id,
        "county_vintage": provider.county_vintage,
        "as_of": provider.as_of,
    }


def share_spm_policy(system):
    """Isolate receipts and variable registration without rebuilding policy.

    An ordinary simulation applies no user reform, so it needs private receipts
    and a private variable registry, not a private copy of the policy itself.
    It is also new rather than cloned, so no previous receipt belongs to it.
    Core's TaxBenefitSystem.clone() rebuilds the whole parameter tree node by
    node and empties both at-instant caches, and this country then deep-copies
    every variable object on top; doing that per household simulation throws
    away the shared instance's warm parameter caches and lands on household API
    request latency.

    Share the parameter tree and its at-instant caches, and reuse the variable
    objects. Every core operation that a reform performs on a variable
    (add_variable, replace_variable, update_variable, neutralize_variable,
    annualize_variable) rebinds ``variables[name]`` to a newly constructed
    object rather than mutating the registered one, so a private dict is enough
    to keep this simulation's registration - including the structural reform
    re-applied at its own start instant - out of the shared instance.
    ``test_ordinary_simulation_shares_default_policy_state`` enforces that
    invariant against the shared instance itself.
    """
    policy = copy(system)
    policy.variables = dict(system.variables)
    policy.spm_forecast_provider = system.spm_forecast_provider.snapshot(
        copy_receipts=False
    )
    return policy


def clone_spm_system(system, *, copy_receipts=True):
    """Clone policy state without reconstructing partially defined reforms.

    Core's Variable.clone() calls the variable class with no baseline metadata,
    losing instance changes such as neutralization and inherited reform fields.
    Let core clone parameters/entities, then copy the actual variable state.
    """
    policy = copy(system)
    policy.variables = {}
    cloned = TaxBenefitSystem.clone(policy)
    by_key = {entity.key: entity for entity in cloned.entities}
    memo = {id(system): cloned, id(system.parameters): cloned.parameters}
    for entity in system.entities:
        memo[id(entity)] = by_key[entity.key]
    for variable in system.variables.values():
        memo[id(variable.entity)] = by_key[variable.entity.key]
    cloned.variables = deepcopy(system.variables, memo)
    cloned.spm_forecast_provider = system.spm_forecast_provider.snapshot(
        copy_receipts=copy_receipts
    )
    return cloned


class SPMSimulationMixin:
    """Keep forecast selection and receipts private to each simulation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Core switches the baseline system after cloning its populations.
        self._rebind_holders()

    def _rebind_holders(self):
        """Bind populations and cached holders to their branch's policy state."""
        self.tax_benefit_system.simulation = self
        variables = self.tax_benefit_system.variables
        for entity in self.tax_benefit_system.entities:
            population = self.populations[entity.key]
            population.entity = entity
            for name, holder in list(population._holders.items()):
                if name in variables:
                    holder.variable = variables[name]
                else:
                    # A reform-only variable has no holder in baseline policy.
                    del population._holders[name]
        # Core shallow-copies this metadata; detach it before pruning inputs
        # that exist only in the reform, so later cache invalidation is valid.
        self._user_input_keys = {
            key for key in self._user_input_keys if key[0] in variables
        }
        self.input_variables = [
            name for name in self.input_variables if name in variables
        ]
        for branch in self.branches.values():
            branch._rebind_holders()

    def apply_reform(self, reform):
        super().apply_reform(reform)
        self._rebind_holders()

    @property
    def spm_config(self):
        return spm_config(self.tax_benefit_system.spm_forecast_provider)

    def spm_provenance(self):
        return self.tax_benefit_system.spm_forecast_provider.provenance()

    def _prepare_spm_system(self, args, kwargs, config, start_instant):
        # Register the shared calculator variables before the input builder sees
        # new primitive role inputs. Cloning also isolates calculation receipts.
        arguments = signature(CoreSimulation.__init__).bind_partial(
            self, *args, **kwargs
        )
        supplied = arguments.arguments.get("tax_benefit_system")
        reform = arguments.arguments.get("reform")
        if supplied is None:
            if reform is not None:
                chosen = self.default_tax_benefit_system(
                    reform=reform, spm=config, start_instant=start_instant
                )
            else:
                # No reform and no supplied system: nothing distinguishes this
                # simulation's policy from the shared instance's, so keep its
                # warm parameter caches instead of rebuilding them.
                chosen = share_spm_policy(self.default_tax_benefit_system_instance)
        elif reform is not None:
            # Core applies the reform set to whatever system it is handed, so
            # the caller's own system must not be the one it reforms.
            chosen = clone_spm_system(supplied, copy_receipts=False)
        else:
            # A caller that builds one system and runs many households through
            # it - the household API among them - keeps that system's warm
            # caches; only receipts and variable registration are private.
            chosen = share_spm_policy(supplied)
        # This is a new simulation, unlike clone() of an already calculated
        # simulation, so no previous calculation receipt belongs to it.
        if config is not None:
            chosen.spm_forecast_provider = create_spm_provider(config)
        arguments.arguments["tax_benefit_system"] = chosen

        # Core constructs a baseline branch for policy reforms. It must use the
        # same SPM selection while retaining baseline tax/benefit policy.
        if reform is not None:
            # The baseline branch holds unreformed policy, which is the shared
            # instance's own policy, so it shares rather than rebuilds it.
            baseline = share_spm_policy(self.default_tax_benefit_system_instance)
            baseline.spm_forecast_provider = chosen.spm_forecast_provider.snapshot()
            self.default_tax_benefit_system_instance = baseline
        # Country dataset interception also needs to see positional datasets.
        return (), {
            key: value for key, value in arguments.arguments.items() if key != "self"
        }

    def clone(self, debug=False, trace=False, clone_tax_benefit_system=True):
        """Retain cached-result receipts while isolating future calculations."""
        cloned = super().clone(debug=debug, trace=trace, clone_tax_benefit_system=False)
        if clone_tax_benefit_system:
            cloned.tax_benefit_system = clone_spm_system(self.tax_benefit_system)
        else:
            # Core branches may share policy state, but each calculation's
            # receipt belongs to that simulation's provider.
            cloned.tax_benefit_system = copy(self.tax_benefit_system)
            cloned.tax_benefit_system.spm_forecast_provider = (
                self.tax_benefit_system.spm_forecast_provider.snapshot(
                    copy_receipts=True
                )
            )
        cloned._rebind_holders()
        return cloned

    def set_input(self, variable_name, period, value):
        # Core's loader calls set_input for every dataset format. Reject saved
        # measurement/resource outputs here without loading the population twice.
        # Household situation overrides remain available for model unit tests;
        # public consumers validate their household input contract separately.
        if (
            getattr(self, "is_over_dataset", False)
            and variable_name in FORMULA_OWNED_INPUTS
        ):
            raise ValueError(
                f"Dataset supplies formula-owned SPM output {variable_name}. "
                "Use primitive inputs and retain observed outputs under report-only names."
            )
        return super().set_input(variable_name, period, value)
