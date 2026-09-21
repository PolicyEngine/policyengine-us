"""Explicit, serializable selection of the canonical SPM forecast.

The calculator owns measurement formulas. The country owns model construction,
input handling and policy resources. Geography is never inferred from a missing
county: callers must explicitly select national or a particular metropolitan area.
"""

import re
from collections.abc import Mapping
from contextlib import contextmanager
from copy import copy, deepcopy
from functools import lru_cache
from inspect import ismethod, signature

import numpy as np

from policyengine_core import periods as periods_
from policyengine_core.simulations import Simulation as CoreSimulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from spm_calculator.errors import SPMInputError
from spm_calculator.policyengine_adapter import (
    FORMULA_OWNED_INPUTS,
    PolicyEngineSPMProvider,
    build_policyengine_variables,
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

# Poverty outputs this country derives from the calculator's measurement.
#
# ``FORMULA_OWNED_INPUTS`` names what the calculator owns: the thresholds, the
# SPM resource total, and the canonical indicators ``poverty_line``,
# ``poverty_gap``, ``spm_unit_is_in_spm_poverty`` and
# ``spm_unit_is_in_deep_spm_poverty``. These names are country-side functions
# of those same values - ``in_poverty`` of the canonical poverty indicator,
# ``deep_poverty_line`` of ``poverty_line``, ``deep_poverty_gap`` of
# ``deep_poverty_line`` and ``spm_unit_net_income``, ``in_deep_poverty`` of
# the canonical deep-poverty indicator, and ``person_in_poverty`` of
# ``in_poverty`` - so a
# dataset column for any of them is an alias for a formula-owned output under a
# name the calculator does not police. Accepting one lets the poverty
# calculation documented in ``docs/usage/microsimulation.md`` and the canonical
# indicator publish different poverty rates for the same population: a dataset
# storing ``in_poverty=[False, False]`` alongside a population every unit of
# which is below its threshold reports 0% and 100% at once.
DERIVED_POVERTY_OUTPUTS = frozenset(
    {
        "deep_poverty_gap",
        "deep_poverty_line",
        "in_deep_poverty",
        "in_poverty",
        "person_in_poverty",
    }
)

# The household-to-SPM-unit housing allocation is computed here, from the
# modelled award and the awarded family's tenant contribution. A dataset that
# stored either quantity would override an allocation the country derives.
SPM_ALLOCATION_OUTPUTS = frozenset(
    {
        "spm_unit_allocated_housing_subsidy",
        "spm_unit_allocated_tenant_payment",
    }
)

# Distribution outputs inherit the same source universe as SPM resources.
SPM_DISTRIBUTION_OUTPUTS = frozenset(
    {"spm_unit_oecd_equiv_net_income", "spm_unit_income_decile"}
)

# Every name a dataset must not store, from either side of the boundary.
REJECTED_DATASET_INPUTS = (
    frozenset(FORMULA_OWNED_INPUTS)
    | DERIVED_POVERTY_OUTPUTS
    | SPM_ALLOCATION_OUTPUTS
    | SPM_DISTRIBUTION_OUTPUTS
)

# This source role has a head/spouse fallback for household situations. A
# population producer must retain its observed boolean instead of treating the
# fallback formula as ownership of the input. This declaration permits source
# delivery; it does not permit synthesizing a default value when data are absent.
# Annual measurement scope is also source-owned despite its household fallback.
DATASET_SOURCE_INPUTS = frozenset(
    {"is_spm_independent_minor_role", "spm_unit_spm_universe_status"}
)

COUNTY_FIPS_PATTERN = re.compile(r"[0-9]{5}")

COUNTY_INPUT_FIX = (
    'send county_fips as a five-digit string (for example "06037"), or select '
    'geography_kind="national" in the spm configuration'
)


def default_spm_universe_status(unit):
    """Household requests describe included units; datasets must declare scope.

    Data origin is a scalar construction contract, not a demographic inference.
    In particular, missing age or tenure never makes a unit outside the universe.
    """
    values = unit.simulation.tax_benefit_system.variables[
        "spm_unit_spm_universe_status"
    ].possible_values
    status = values.UNRESOLVED if unit.simulation.is_over_dataset else values.INCLUDED
    return unit.filled_array(status.index)


def spm_universe_mask(unit, period):
    """Require a resolved source decision and return included unit positions."""
    status = unit("spm_unit_spm_universe_status", period).decode_to_str()
    if np.any(status == "UNRESOLVED"):
        raise SPMInputError(
            "SPM_UNIVERSE_REQUIRED",
            "Declare INCLUDED or OUTSIDE for every SPM unit from the source "
            "measurement universe; unresolved units cannot be measured.",
        )
    return status == "INCLUDED"


def scoped_spm_amount(unit, period, field):
    """Keep outside amounts missing and never pass those units to the provider."""
    included = spm_universe_mask(unit, period)
    amounts = masked_policyengine_amount(unit, period, field, included)
    return np.where(included, amounts, np.nan)


def country_spm_variables():
    """Apply country-owned scope to the calculator's registered amount fields."""
    fields = {
        "spm_unit_reference_spm_threshold": "reference_threshold",
        "spm_unit_unadjusted_spm_threshold": "unadjusted_threshold",
        "spm_unit_geographic_adjustment": "geographic_factor",
        "spm_unit_spm_threshold": "threshold",
        "spm_unit_spm_threshold_housing_portion": "housing_portion",
    }

    def formula_for(field):
        def formula(unit, period, parameters):
            return scoped_spm_amount(unit, period, field)

        return formula

    variables = build_policyengine_variables()
    for variable in variables:
        if variable.__name__ in fields:
            # The calculator creates fresh classes for each system. Only the
            # selection changes; its provider still owns every final amount.
            variable.formula = formula_for(fields[variable.__name__])
    return variables


def nullable_spm_indicator(unit, period, income, threshold):
    """Return 0/1 for measured units, NaN outside, and reject invalid inputs."""
    included = spm_universe_mask(unit, period)
    if (
        not np.isfinite(income[included]).all()
        or not np.isfinite(threshold[included]).all()
        or np.any(threshold[included] <= 0)
    ):
        raise SPMInputError(
            "SPM_MEASUREMENT_INVALID",
            "Included units require finite resources and positive finite thresholds.",
        )
    result = np.full(included.shape, np.nan)
    result[included] = income[included] < threshold[included]
    return result


def is_county_fips(value):
    """Accept only a five-digit county FIPS code, supplied as text.

    The advertised contract is a five-digit *string*. Stringifying whatever
    arrived enforced the digit count alone, so an integer whose decimal form
    happens to be five digits (``36061``) passed, while the same mistake for a
    state whose code carries a leading zero (``6037``, meaning Los Angeles
    County ``06037``) failed - one silently accepted, the other reported as an
    absent county. Reject every non-text value here instead, so an integer
    county code, a pandas missing value and a truncated code all fail the same
    way and name the same fix.

    ``numpy.str_`` and ``numpy.bytes_`` subclass ``str`` and ``bytes``, so a
    county read back out of the model - which stores ``county_fips`` as text -
    is still accepted. A within-state CPS code such as ``5`` and a missing
    value such as ``nan`` fail as an absent county rather than an unrecognised
    one, whichever type they arrive as.
    """
    if isinstance(value, bytes):
        value = value.decode()
    if not isinstance(value, str):
        return False
    return COUNTY_FIPS_PATTERN.fullmatch(value) is not None


class CountyRequiringSPMProvider(PolicyEngineSPMProvider):
    """Name the caller's fix when a county selection has no usable county.

    The calculator reports an absent county only for ``None`` and the empty
    string, and reports anything else as an unavailable county. A legacy
    population file storing the CPS within-state integer code, or a household
    request sending an integer or a missing value, would otherwise be told its
    county assignment is unavailable, which points at the artifact instead of
    at the input.

    This provider also remembers which counties the model was handed as
    something other than text. ``county_fips`` declares ``value_type = str``,
    but core maps ``str`` to the numpy ``object`` dtype, so the model stores
    whatever it is given and an integer column stays integers - and both
    readers of that column stringify before calling a provider. An integer
    county code for a state without a leading zero therefore arrived here
    indistinguishable from the same code sent correctly as a string, and was
    silently accepted, while the same mistake for California (``6037`` for Los
    Angeles County ``06037``) was reported as an absent county. Recording the
    input's type at the one point that still sees it, and rejecting it when a
    county measurement actually needs that county, makes the two fail the same
    way without demanding SPM geography from a caller who never asks for it.
    """

    def __post_init__(self):
        super().__post_init__()
        # The base is a frozen dataclass, so this receipt of input types is
        # attached rather than declared. It maps (year, county text) to the
        # repr of what was actually supplied, and ``record_county_input_types``
        # replaces a year's entries outright, so correcting an input clears it.
        object.__setattr__(self, "_untyped_counties", {})

    def snapshot(self, *, copy_receipts=False):
        snapshot = super().snapshot(copy_receipts=copy_receipts)
        if copy_receipts:
            # A new simulation re-reads its own inputs; only a clone, which
            # keeps this simulation's holders, inherits what they held.
            snapshot._untyped_counties.update(self._untyped_counties)
        return snapshot

    def record_county_input_types(self, year, values):
        """Replace this year's record of counties not supplied as text.

        Replacing rather than accumulating is what lets a caller correct the
        input: re-setting ``county_fips`` for a period re-derives the record
        for that period from what the model now holds.
        """
        if self.geography_kind != "county":
            # Nothing will ask this provider for a county.
            return
        untyped = self._untyped_counties
        for key in [key for key in untyped if key[0] == year]:
            del untyped[key]
        for value in values:
            if not isinstance(value, (str, bytes)):
                untyped[(year, str(value))] = repr(value)

    def with_county_input_types(self, year, values):
        """Validate selected inputs without replacing simulation-wide receipts.

        An excluded numeric county can spell the same FIPS as an included text
        county. Only the selected raw inputs constrain this measurement. Share
        the canonical amount cache and provenance with the simulation, while
        keeping this view's typing receipt private.
        """
        selected = copy(self)
        object.__setattr__(selected, "_untyped_counties", self._untyped_counties.copy())
        selected.record_county_input_types(year, values)
        return selected

    def require_county_input(self, year, county_fips):
        """Reject a county this provider cannot honour as a five-digit string."""
        if self.geography_kind != "county":
            return
        if is_county_fips(county_fips):
            supplied = self._untyped_counties.get((year, county_fips))
            if supplied is None:
                return
            # The county reaching a provider has already been stringified by
            # the variable that read the column, so this is as precise as the
            # rejection gets: every request for this county in this year
            # fails, not only the household whose input was mistyped.
            raise SPMInputError(
                "SPM_GEOGRAPHY_REQUIRED",
                f"County {county_fips} was supplied for {year} as {supplied}, "
                f"not as text: {COUNTY_INPUT_FIX}",
            )
        raise SPMInputError(
            "SPM_GEOGRAPHY_REQUIRED",
            f"County selection has no county FIPS input ({county_fips!r}): "
            f"{COUNTY_INPUT_FIX}",
        )

    def _amounts(self, year, adults, children, tenure, county):
        # Check before the memo, so a cache entry filled by a correctly typed
        # row cannot let an identically spelled untyped row through.
        self.require_county_input(year, county)
        return super()._amounts(year, adults, children, tenure, county)

    def calculate_unit(self, *, year, adults, children, tenure, county_fips=None):
        self.require_county_input(year, county_fips)
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
        bound = bound.with_county_input_types(int(period.start.year), counties)
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


SHARED_TREE_MARK = "_spm_tree_is_shared"


def mark_tree_shared(tree):
    """Record that more than one system can now read this parameter tree.

    Ownership is tracked on the tree rather than on the systems reading it,
    because a system's own history says nothing about who else holds the tree
    it is pointing at: a system that took a private copy, and then lent it to a
    second simulation, must stop writing to that copy in place. The mark is
    one-way. Dropping it would need to know when the last other reader went
    away, and a tree wrongly believed private is silently shared state, while a
    tree wrongly believed shared only costs one clone.
    """
    if tree is not None:
        setattr(tree, SHARED_TREE_MARK, True)
    return tree


def unmark_tree_shared(tree):
    """Record that this tree has exactly one reader.

    Core's ``ParameterNode.clone`` copies the node's instance dictionary, so a
    clone taken from a shared tree arrives carrying the mark even though it is
    brand new and private.
    """
    if tree is not None:
        setattr(tree, SHARED_TREE_MARK, False)
    return tree


def tree_is_shared(tree):
    return tree is not None and getattr(tree, SHARED_TREE_MARK, False)


SHARED_POLICY_BASES = {}


def shared_policy_class(base):
    """Return the shared-parameter subclass of ``base``, creating it once.

    ``share_spm_policy`` hands back a system whose parameter tree belongs to
    someone else, so the tree needs a read barrier that a plain attribute
    cannot provide. Subclassing keeps that barrier off every other system: an
    independently built ``CountryTaxBenefitSystem`` is untouched.
    """
    if getattr(base, "shared_policy_base", None) is not None:
        # Already a shared-policy class: sharing a shared system is idempotent.
        return base
    created = SHARED_POLICY_BASES.get(base)
    if created is None:
        name = f"SharedParameter{base.__name__}"
        if name in globals():
            # Two bases sharing a class name would otherwise publish one class
            # under the other's name, and pickle would restore the wrong one.
            name = f"{name}{len(SHARED_POLICY_BASES) + 1}"
        created = type(
            name, (SharedParameterPolicy, base), {"shared_policy_base": base}
        )
        # Publish it under its own name so a system built from it still pickles:
        # a class only reachable from a dictionary has no import path.
        created.__module__ = __name__
        created.__qualname__ = name
        globals()[name] = created
        SHARED_POLICY_BASES[base] = created
    return created


class SharedParameterPolicy:
    """Policy state that borrows another system's parameter tree.

    Reading parameters through this system costs nothing: the tree and its warm
    at-instant caches are the lending system's own. Writing to it must not
    happen at all, because core applies a reform to whatever tree the system
    hands it - ``Simulation.apply_reform`` calls ``reform.apply(system)``
    directly, bypassing ``Reform.__init__``'s defensive clone - and a mutated
    shared tree changes unrelated simulations, including ones already built.

    So the tree is copy-on-write. Reform application arms the read barrier;
    the first read of ``parameters`` inside that window takes a private clone
    through core, leaving the lending system's tree and warm caches untouched.
    Cloning rebuilds every node of a 130,000-parameter tree and takes seconds,
    which is why it is deferred to the reforms that actually reach the tree:
    the structural reform that every simulation re-applies at its own start
    instant only rebinds variables, so it never reads ``parameters`` and never
    pays for a clone.
    """

    shared_policy_base = None

    @property
    def parameters(self):
        if self.__dict__.get("detaching_shared_parameters", False):
            self.detach_parameters()
        return self.__dict__["shared_parameters"]

    @parameters.setter
    def parameters(self, value):
        self.__dict__["shared_parameters"] = value

    @property
    def shares_parameters(self):
        """Whether anything but this system can see writes to this tree."""
        return tree_is_shared(self.__dict__["shared_parameters"])

    @property
    def detaching_shared_parameters(self):
        """Whether a reform is being applied to this system right now."""
        return self.__dict__.get("detaching_shared_parameters", False)

    def detach_parameters(self):
        """Take a private copy of the shared tree; report whether one was made."""
        tree = self.__dict__["shared_parameters"]
        if tree is None or not tree_is_shared(tree):
            return False
        # Clear the barrier first: cloning reads the tree through core, and
        # that read must not re-enter this method.
        self.__dict__["detaching_shared_parameters"] = False
        self.__dict__["shared_parameters"] = unmark_tree_shared(tree.clone())
        # The lender keeps its warm at-instant cache; this system starts cold
        # because its parameter values are about to differ.
        self._parameters_at_instant_cache = {}
        return True

    @contextmanager
    def detaching_parameters(self):
        """Arm the copy-on-write barrier for the duration of a reform."""
        previous = self.__dict__.get("detaching_shared_parameters", False)
        self.__dict__["detaching_shared_parameters"] = True
        try:
            yield
        finally:
            self.__dict__["detaching_shared_parameters"] = previous

    def apply_reform_set(self, reform):
        # Core applies a reform to this system's own tree, so detach first
        # however the reform arrives.
        with self.detaching_parameters():
            return super().apply_reform_set(reform)

    def modify_parameters(self, modifier_function):
        # The documented way for a reform to edit parameters, and core hands
        # the live tree to the modifier rather than a copy.
        self.detach_parameters()
        return super().modify_parameters(modifier_function)

    def load_extension(self, extension):
        # Core merges the extension's parameters into this tree in place.
        self.detach_parameters()
        return super().load_extension(extension)

    def add_abolition_parameters(self):
        # Core adds an abolition child per variable, in place.
        self.detach_parameters()
        return super().add_abolition_parameters()

    def clone(self):
        # Core's clone writes the cloned tree into the new instance's
        # dictionary, where this class's property shadows it, so hand it an
        # ordinary instance and let the base decide how to clone.
        return type(self).shared_policy_base.clone(self.unshared_copy())

    def unshared_copy(self):
        """A plain shallow copy holding the tree as an ordinary attribute.

        Core's ``TaxBenefitSystem.clone`` writes the cloned tree straight into
        the new instance's ``__dict__`` under ``parameters``, which this class's
        property would shadow, so anything that clones through core starts from
        an ordinary instance instead.
        """
        policy = copy(self)
        tree = policy.__dict__.pop("shared_parameters", None)
        policy.__dict__.pop("shares_parameters_with_lender", None)
        policy.__dict__.pop("detaching_shared_parameters", None)
        policy.__class__ = type(self).shared_policy_base
        policy.parameters = tree
        return policy


def plain_policy_copy(system):
    """Shallow-copy any system into one that holds its tree as an attribute."""
    if isinstance(system, SharedParameterPolicy):
        return system.unshared_copy()
    return copy(system)


def with_parameter_barrier(system):
    """Give ``system`` a copy-on-write parameter tree, in place.

    Every simulation's own system carries the barrier, not only the ones that
    borrow the shipped policy, because the tree a simulation starts out owning
    can acquire other readers later - a branch copies the system, and another
    simulation can be built on it - and from then on a reform must clone
    before it writes. Whether anyone else is reading is recorded on the tree
    (see :func:`mark_tree_shared`), so installing the barrier costs nothing
    and changes nothing on its own.
    """
    if isinstance(system, SharedParameterPolicy):
        return system
    system.__class__ = shared_policy_class(type(system))
    system.__dict__["shared_parameters"] = system.__dict__.pop("parameters", None)
    system.__dict__["detaching_shared_parameters"] = False
    return system


def bind_private_entities(policy):
    """Give ``policy`` its own Entity objects, bound to its own registry.

    An Entity resolves variable names through the system it is bound to
    (``Entity.get_variable``), and a population asks its entity before reading
    or creating a holder. Sharing the lending system's entities therefore sent
    every holder lookup to the lending system's registry, so a variable that a
    reform added to this system's private registry was invisible to
    ``set_input``, which raised ``VariableNotFoundError`` for a variable the
    system plainly had.

    Core's own constructor and ``clone`` copy entities for the same reason.
    Unlike ``clone``, keep ``person_entity`` and ``group_entities`` pointing at
    the very objects in ``entities``, so there is exactly one entity object per
    key to rebind.
    """
    entities = [copy(entity) for entity in policy.entities]
    by_key = {entity.key: entity for entity in entities}
    policy.entities = entities
    policy.person_entity = by_key[policy.person_entity.key]
    policy.group_entities = [by_key[entity.key] for entity in policy.group_entities]
    policy.group_entity_keys = [entity.key for entity in policy.group_entities]
    for entity in entities:
        entity.set_tax_benefit_system(policy)
    return policy


def isolate_parameter_tracing(system, tracer, branch_name):
    """Give ``system`` its own root parameter node, primed for ``tracer``.

    Core marks a traced request by writing that request's tracer, trace flag
    and branch name onto the root node of the parameter tree, and the root then
    caches the resulting ``TracingParameterNodeAtInstant`` in its own
    at-instant cache. On a shared tree the second request reuses the first
    request's cached tracing node, so its parameter accesses are recorded
    against the first request's tracer - or, once that request's trace frame
    has closed, recorded nowhere at all - and the shared tree is left holding a
    finished request's tracer for every simulation that reads it afterwards.

    Only the root carries those fields: children are wrapped on the fly from
    the root's tracing node and cache plain at-instant nodes. A shallow copy of
    the root - the same children, its own at-instant cache and its own trace
    fields - therefore isolates a request's parameter receipts completely, and
    costs microseconds rather than the seconds a full tree clone takes. The
    children stay shared, so a later reform still detaches the whole tree.

    Prime the copy as traced rather than waiting for core to mark it. Core sets
    those fields in ``_run_formula``, but ``_calculate`` reads
    ``parameters(period).gov.abolitions`` first, so the at-instant node for
    each period is built and cached before the tree is ever marked as traced
    and no parameter access is recorded at all.
    """
    root = system.parameters
    if root is None:
        return None
    if tree_is_shared(root):
        private = copy(root)
        private._at_instant_cache = {}
        # The copy shares the original's children, and each child's parent
        # still points at the original root, so an edit made through a child
        # would clear the original's at-instant cache and leave this one
        # stale. Mark the copy shared: any write detaches a real clone first.
        mark_tree_shared(private)
        system.parameters = private
        system._parameters_at_instant_cache = {}
        root = private
    else:
        # Nobody else reads this tree, so it can be marked traced where it
        # stands - and leaving it in place keeps each parameter's parent
        # pointing at the root whose at-instant cache an edit has to clear.
        root._at_instant_cache = {}
        system._parameters_at_instant_cache = {}
    root.trace = True
    root.tracer = tracer
    root.branch_name = branch_name
    return root


def share_spm_policy(system):
    """Isolate receipts and variable registration without rebuilding policy.

    An ordinary simulation applies no user reform, so it needs private
    receipts, a private variable registry and private entities to resolve that
    registry - not a private copy of the policy itself. It is also new rather
    than cloned, so no previous receipt belongs to it.

    Core's ``TaxBenefitSystem.clone()`` rebuilds the whole parameter tree node
    by node and empties both at-instant caches, and this country then
    deep-copies every variable object on top; doing that per household
    simulation throws away the shared instance's warm parameter caches and
    lands on household API request latency.

    So share the parameter tree and its at-instant caches, and reuse the
    variable objects. Every core operation that a reform performs on a variable
    (add_variable, replace_variable, update_variable, neutralize_variable,
    annualize_variable) rebinds ``variables[name]`` to a newly constructed
    object rather than mutating the registered one, so a private dict is enough
    to keep this simulation's registration - including the structural reform
    re-applied at its own start instant - out of the shared instance.
    ``test_ordinary_simulation_shares_default_policy_state`` enforces that
    invariant against the shared instance itself.

    A reform that reaches the parameter tree has no such protection, so the
    returned system takes a private copy of the tree the first time a reform
    reads it: see :class:`SharedParameterPolicy`.
    """
    policy = copy(system)
    policy.variables = dict(system.variables)
    bind_private_entities(policy)
    with_parameter_barrier(policy)
    # The lender is now one reader among several, so neither side may write to
    # this tree in place - including a lender that had taken a private copy.
    mark_tree_shared(policy.__dict__["shared_parameters"])
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
    policy = plain_policy_copy(system)
    policy.variables = {}
    cloned = TaxBenefitSystem.clone(policy)
    unmark_tree_shared(cloned.parameters)
    # Core copies ``entities``, ``person_entity`` and ``group_entities``
    # separately, leaving two objects per group entity key; keep one, so a
    # rebind reaches every reader of that entity.
    by_key = {entity.key: entity for entity in cloned.entities}
    cloned.person_entity = by_key[cloned.person_entity.key]
    cloned.group_entities = [by_key[entity.key] for entity in cloned.group_entities]
    cloned.group_entity_keys = [entity.key for entity in cloned.group_entities]
    for entity in cloned.entities:
        entity.set_tax_benefit_system(cloned)
    memo = {id(system): cloned, id(system.parameters): cloned.parameters}
    for entity in system.entities:
        memo[id(entity)] = by_key[entity.key]
    for variable in system.variables.values():
        memo[id(variable.entity)] = by_key[variable.entity.key]
    cloned.variables = deepcopy(system.variables, memo)
    cloned.spm_forecast_provider = system.spm_forecast_provider.snapshot(
        copy_receipts=copy_receipts
    )
    # A clone owns its tree outright, but it does not keep it to itself: a
    # branch copies the system, and another simulation can be built on it, at
    # which point a reform must clone before it writes. ``plain_policy_copy``
    # strips the barrier so core can clone through an ordinary instance, so
    # put it back - without it, a branch of a clone rewrites the clone's own
    # policy, which is the defect this class exists to prevent.
    with_parameter_barrier(cloned)
    return cloned


class SPMSimulationMixin:
    """Keep forecast selection and receipts private to each simulation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Core switches the baseline system after cloning its populations.
        self._rebind_holders()
        # Core sets ``trace`` before this simulation owns its policy state.
        self._isolate_parameter_tracing()
        # Every input path - situation builder, dataset loader, direct
        # set_input - has landed in the holder by now.
        self._record_county_input_types()

    @property
    def trace(self):
        return CoreSimulation.trace.fget(self)

    @trace.setter
    def trace(self, trace):
        CoreSimulation.trace.fset(self, trace)
        self._isolate_parameter_tracing()

    def _isolate_parameter_tracing(self):
        """Stop a traced request writing its tracer onto shared parameters."""
        if not self.trace:
            return
        policy = getattr(self, "tax_benefit_system", None)
        # Core sets ``trace`` before a new simulation owns its policy state,
        # both while constructing one and while cloning one, so leave the
        # original's system alone until this simulation has claimed its own.
        if policy is not None and getattr(policy, "simulation", None) is self:
            isolate_parameter_tracing(policy, self.tracer, self.branch_name)
        for branch in getattr(self, "branches", {}).values():
            branch._isolate_parameter_tracing()

    def get_branch(self, name="branch", clone_system=False):
        branch = super().get_branch(name, clone_system)
        # Core names the branch and hands it this simulation's tracer after
        # cloning, so re-prime the branch's root with what it ended up holding.
        branch._isolate_parameter_tracing()
        return branch

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
        policy = self.tax_benefit_system
        detaching = getattr(policy, "detaching_parameters", None)
        if detaching is None or policy.detaching_shared_parameters:
            # Either an ordinary system, or core recursing through a tuple of
            # reforms into this override again. Reading ``parameters`` inside
            # the armed window would itself trip the barrier and clone the
            # tree, which is exactly what a variable-only reform must not pay.
            super().apply_reform(reform)
            self._rebind_holders()
            return
        previous_children = getattr(policy.parameters, "children", None)
        with detaching():
            super().apply_reform(reform)
        self._adopt_detached_parameters(previous_children)
        # A detached tree is a fresh root, carrying none of the trace state
        # core wrote onto the one it replaced.
        self._isolate_parameter_tracing()
        self._rebind_holders()

    def _adopt_detached_parameters(self, previous_children):
        """Move branches off the pre-reform tree onto the detached copy.

        A branch created with ``clone_system=False`` shares its parent's policy
        state deliberately, so a reform the parent applies is a reform the
        branch runs under. Detaching would otherwise strand the branch on the
        unreformed tree.

        Branches are recognised by the children of their root node rather than
        by the root itself, because a traced branch holds a shallow copy of the
        root with those same children (see ``isolate_parameter_tracing``) and
        would never match on identity. An adopting branch keeps sharing - the
        tree now has more than one reader, so its own reform must detach rather
        than rewrite its parent's policy.
        """
        detached = self.tax_benefit_system.parameters
        if detached is None or detached.children is previous_children:
            return
        cache = self.tax_benefit_system._parameters_at_instant_cache
        for name, branch in self.branches.items():
            if name == "baseline":
                # The baseline branch holds unreformed policy by construction.
                continue
            policy = branch.tax_benefit_system
            tree = getattr(policy, "parameters", None)
            if tree is not None and tree.children is previous_children:
                # The detached tree now has a second reader.
                mark_tree_shared(detached)
                policy.parameters = detached
                policy._parameters_at_instant_cache = cache
                # A traced branch needs its own root back, with its own
                # at-instant cache, or its parameter receipts rejoin the
                # parent's.
                branch._isolate_parameter_tracing()
            branch._adopt_detached_parameters(previous_children)

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
                chosen = with_parameter_barrier(
                    self.default_tax_benefit_system(
                        reform=reform, spm=config, start_instant=start_instant
                    )
                )
            else:
                # No reform and no supplied system: nothing distinguishes this
                # simulation's policy from the shared instance's, so keep its
                # warm parameter caches instead of rebuilding them.
                chosen = share_spm_policy(self.default_tax_benefit_system_instance)
        elif reform is not None:
            # Core applies the reform set to whatever system it is handed, so
            # the caller's own system must not be the one it reforms.
            chosen = with_parameter_barrier(
                clone_spm_system(supplied, copy_receipts=False)
            )
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
            # Two systems now read this tree, so neither may write to it in
            # place: a branch's reform must not rewrite its parent's policy.
            mark_tree_shared(getattr(cloned.tax_benefit_system, "parameters", None))
            cloned.tax_benefit_system.spm_forecast_provider = (
                self.tax_benefit_system.spm_forecast_provider.snapshot(
                    copy_receipts=True
                )
            )
        cloned._rebind_holders()
        self._rebind_method_aliases(cloned)
        cloned._isolate_parameter_tracing()
        return cloned

    def _rebind_method_aliases(self, cloned):
        """Point copied bound-method aliases at the clone, not the original.

        Core keeps backwards-compatibility aliases as bound methods on the
        instance (``self.calc = self.calculate``, ``self.df =
        self.calculate_dataframe``) and its ``clone`` copies the instance
        dictionary verbatim, so every alias on the clone still called the
        original simulation. ``clone.calc(...)`` therefore returned the
        original's values under the original's policy, and recorded the
        original's SPM receipts, while ``clone.calculate(...)`` - documented as
        the same call - returned the clone's. Rebind by method name so an alias
        core adds later is repaired too.
        """
        for name, value in list(cloned.__dict__.items()):
            if ismethod(value) and value.__self__ is self:
                cloned.__dict__[name] = getattr(cloned, value.__func__.__name__)

    def _record_county_input_types(self, period=None):
        """Tell this simulation's providers which counties were not text.

        The county a provider is asked for has already been stringified by the
        variable that reads the column, so the type has to be captured here,
        where the stored input is still whatever the caller supplied. Record it
        on this simulation's own provider and on its branches', because a
        reform simulation's baseline arm is handed a separate provider that
        never sees an input of its own.
        """
        holder = self.get_holder("county_fips")
        periods = (
            holder.get_known_periods() if period is None else [periods_.period(period)]
        )
        for known_period in periods:
            array = holder.get_array(known_period)
            if array is None or array.dtype.kind in "SU":
                # A real text dtype cannot be hiding an integer.
                continue
            year = int(known_period.start.year)
            for simulation in self._simulation_family():
                record = getattr(
                    simulation.tax_benefit_system.spm_forecast_provider,
                    "record_county_input_types",
                    None,
                )
                if record is not None:
                    record(year, array)

    def _simulation_family(self):
        """This simulation and every branch that reads the same inputs."""
        yield self
        for branch in getattr(self, "branches", {}).values():
            yield from branch._simulation_family()

    def set_input(self, variable_name, period, value):
        # Core's loader calls set_input for every dataset format. Reject saved
        # measurement/resource outputs here without loading the population twice.
        # Household situation overrides remain available for model unit tests;
        # public consumers validate their household input contract separately.
        if (
            getattr(self, "is_over_dataset", False)
            and variable_name in REJECTED_DATASET_INPUTS
        ):
            raise ValueError(
                f"Dataset supplies formula-owned SPM output {variable_name}. "
                "Use primitive inputs and retain observed outputs under report-only names."
            )
        result = super().set_input(variable_name, period, value)
        if variable_name in DATASET_SOURCE_INPUTS:
            # Scope and observed roles govern cached measurements and summaries.
            # Core preserves explicit inputs while clearing dependent results.
            self._invalidate_all_caches()
        if variable_name == "county_fips":
            self._record_county_input_types(period)
        return result
