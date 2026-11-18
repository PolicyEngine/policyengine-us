import hashlib
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_us.entities import *
from policyengine_us.parameters.gov.irs.uprating import (
    set_irs_uprating_parameter,
)
from policyengine_core.simulations import (
    Simulation as CoreSimulation,
    Microsimulation as CoreMicrosimulation,
    IndividualSim as CoreIndividualSim,
)
from policyengine_us.variables.household.demographic.geographic.state.in_state import (
    create_50_state_variables,
)
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)
from policyengine_us.tools.parameters import (
    EARLIEST_STRUCTURAL_REFORM_YEAR,
    FIRST_MODELED_YEAR,
    backdate_parameters,
)
from policyengine_us.reforms import create_structural_reforms_from_parameters
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    PRE_RESPONSE_INPUTS,
)
from policyengine_core.parameters.operations.homogenize_parameters import (
    homogenize_parameter_structures,
)
from policyengine_core.parameters.operations.interpolate_parameters import (
    interpolate_parameters,
)
from policyengine_core.parameters.operations.propagate_parameter_metadata import (
    propagate_parameter_metadata,
)
from policyengine_core.parameters.operations.uprate_parameters import (
    uprate_parameters,
)
from .tools.default_uprating import add_default_uprating
from .tools.marital_units import infer_missing_marital_units
from .tools.tob import TobCalculationMixin
from .tools.period_branch import delete_input_values
from .tools.social_security_inputs import (
    install_social_security_input_compatibility,
    migrate_social_security_inputs,
)
from .tools.section_911 import validate_section_911_batch_inputs
from .tools.per_capita_uprating import (
    add_per_capita_parameters_for_parameter_uprating,
    add_per_capita_uprating,
    derived_per_capita_series,
    detached_copy,
    is_national_total_path,
    per_capita_nodes_unchanged,
    remove_per_capita_series,
    restore_child_order,
    restore_per_capita_series,
)
from policyengine_us.data.dataset_schema import (
    _DEFAULT_TIME_PERIOD,
    US_ENTITIES,
    USSingleYearDataset,
    USMultiYearDataset,
)

from typing import Annotated
from spm_calculator.policyengine_adapter import build_policyengine_variables
from policyengine_us.spm import (
    SHARED_TREE_MARK,
    SPMSimulationMixin,
    bind_private_entities,
    clone_spm_system,
    create_spm_provider,
    plain_policy_copy,
)

install_social_security_input_compatibility()

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2026
# Structural-reform checks start here rather than at CURRENT_YEAR, so moving the
# default calculation year does not stop reforms from earlier years applying.
DEFAULT_START_DATE = f"{EARLIEST_STRUCTURAL_REFORM_YEAR}-01-01"

# Certified Microcosm build (primary-source US microdata), pinned by build id.
# Microcosm ships from a Hugging Face *dataset* repo, hence the `hf://datasets/`
# prefix handled in `_resolve_dataset_path`.
DEFAULT_DATASET = "hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-spm-20260909"
# Content hash of the certified build the default URI must resolve to.
#
# A Hugging Face tag is a mutable pointer: re-tagging the repository, or a
# truncated or substituted download, would hand the model another schema-valid
# H5 and change every standalone-country result with no rejection anywhere.
# Only the country's own default is checked - an explicit `dataset=` argument
# names the caller's own artifact and remains the caller's responsibility.
DEFAULT_DATASET_SHA256 = (
    "6496cc4393d4d3c6574f76eca231de5898c803b9067645591fd5c4d3e65aee84"
)


@dataclass(frozen=True, eq=False)
class UnreformedBuild:
    """What a system built without a reform records to derive reform systems.

    It holds no reference to the system, so a copy or clone that carries it
    does not keep the original's parameter tree alive.
    """

    # The registry before the structural reforms and per-state variables.
    variables_before_reforms: dict
    # Copies, taken at the same point, of the variables in that registry that
    # uprate by a national total. ``add_per_capita_uprating`` later points the
    # registry's own objects at the per-capita series in place.
    total_uprated_variables: dict
    # The per-capita series ``add_per_capita_uprating`` added to the tree
    # after that point, and copies, as they stood at that point, of those it
    # replaced when it refreshed them.
    per_capita_series_added: frozenset
    per_capita_series_replaced: dict
    # The order of the children of each node holding a replaced series, at
    # that point: a refresh moves the series to the end of its parent.
    per_capita_parent_child_order: dict
    # The children of those nodes when construction finished.
    per_capita_parent_children: dict
    # The registry when construction finished.
    variables: dict


class CountryTaxBenefitSystem(TaxBenefitSystem):
    """
    The tax-benefit system for the United States.
    This structure is a modification of the -core
    package's base TaxBenefitSystem class.

    Args:
        reform (tuple | None): A tuple of reforms to apply to the system.
        If no reform is applied, the system will be initialized with the
        default tax/benefit parameters.

        start_instant(str: ISO date format YYYY-MM-DD): Optional; The first
        date checked when deciding which structural reforms apply; defaults
        to 2024-01-01. Most structural reforms are checked on January 1 of
        ten consecutive years from this date, and some only on this date, so
        set it when a reform's parameter turns on outside those dates.
    """

    variables_dir = COUNTRY_DIR / "variables"
    _social_security_input_compatibility = True
    auto_carry_over_input_variables = True
    basic_inputs = [
        "state_name",
        "employment_income",
        "age",
    ]
    modelled_policies = COUNTRY_DIR / "programs.yaml"

    def preprocess_situation(self, situation, default_period=None):
        return infer_missing_marital_units(situation, default_period, self)

    def __init__(
        self,
        reform: tuple | None = None,
        start_instant: Annotated[
            str, "ISO date format YYYY-MM-DD"
        ] = DEFAULT_START_DATE,
        spm: dict | None = None,
    ):
        super().__init__(entities, reform=reform)
        self.spm_forecast_provider = create_spm_provider(spm)
        self.add_variables(*build_policyengine_variables())
        self.load_parameters(COUNTRY_DIR / "parameters")
        self.add_abolition_parameters()
        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = homogenize_parameter_structures(
            self.parameters, self.variables
        )
        self.parameters = propagate_parameter_metadata(self.parameters)
        self.parameters = interpolate_parameters(self.parameters)
        add_per_capita_parameters_for_parameter_uprating(self.parameters)
        self.parameters = uprate_parameters(self.parameters)
        self.parameters = propagate_parameter_metadata(self.parameters)
        add_default_uprating(self)

        # Backdated before any reform is applied. Backdating copies each
        # parameter's earliest value back to the start of FIRST_MODELED_YEAR,
        # so on a parameter first dated after that it would copy a reform
        # value that starts on or before that first date back to that year,
        # and a reform ending before that date would leave the years between
        # the two undefined.
        self.parameters = backdate_parameters(
            self.parameters, first_instant=f"{FIRST_MODELED_YEAR}-01-01"
        )

        # Preserve the processed current-law path before user reforms can
        # remove/change the payroll cap. Owners' draw can keep this ceiling
        # independently or explicitly select no ceiling.
        draw_cap = self.parameters.gov.irs.payroll.social_security.cap.clone()
        draw_cap.name = "gov.contrib.ssa.owners_draw.current_law_cap"
        draw_cap.metadata.update(
            label="Current-law OASDI cap preserved for owners' draw", economy=False
        )
        draw_cap.metadata.pop("uprating", None)
        self.parameters.gov.contrib.ssa.owners_draw.add_child(
            "current_law_cap", draw_cap
        )

        # Nothing above depends on the reform. A system built without one
        # records its policy as it stands here, before the structural reforms,
        # the per-state variables and the per-capita series, so that a reform
        # system can be derived from it by running only the steps below. An
        # empty reform counts as a reform here, as it does for a simulation,
        # which derives its system whenever its reform is not None.
        if reform is not None:
            self._apply_reforms(reform, start_instant)
            self._unreformed_build = None
            return
        variables_before_reforms = dict(self.variables)
        total_uprated_variables = {
            name: variable.clone()
            for name, variable in variables_before_reforms.items()
            if is_national_total_path(variable.uprating)
        }
        series_before = derived_per_capita_series(self.parameters)
        series_copies = {
            path: detached_copy(series) for path, series in series_before.items()
        }
        child_order_before = {
            parent_path: tuple(self.parameters.get_child(parent_path).children)
            for parent_path in {path.rpartition(".")[0] for path in series_before}
        }
        self._apply_reforms(reform, start_instant)
        series_after = derived_per_capita_series(self.parameters)
        series_replaced = {
            path: series_copies[path]
            for path, series in series_before.items()
            if series_after.get(path) is not series
        }
        self._unreformed_build = UnreformedBuild(
            variables_before_reforms=variables_before_reforms,
            total_uprated_variables=total_uprated_variables,
            per_capita_series_added=frozenset(
                series_after.keys() - series_before.keys()
            ),
            per_capita_series_replaced=series_replaced,
            per_capita_parent_child_order={
                parent_path: child_order_before[parent_path]
                for parent_path in {path.rpartition(".")[0] for path in series_replaced}
            },
            per_capita_parent_children={
                parent_path: frozenset(self.parameters.get_child(parent_path).children)
                for parent_path in {path.rpartition(".")[0] for path in series_replaced}
            },
            variables=dict(self.variables),
        )

    def _apply_reforms(self, reform, start_instant):
        """Apply ``reform`` and the structural reforms to processed policy.

        These are the steps of construction that depend on the reform, so
        ``derive_reform_system`` runs them on a copy of an unreformed system.
        """
        if reform:
            # Applied after the parameter processing pipeline so that values
            # a reform inserts at future dates cannot act as defined values
            # during uprating/interpolation, which would freeze the years
            # between the last legislated value and the reform start at the
            # last legislated nominal value (issue #9075) — and before
            # structural-reform detection, which reads reformed parameter
            # values.
            self.apply_reform_set(reform)
            # Backdates parameters the reform added or replaced, as before.
            # Those it only updated already have a value dated by the start of
            # FIRST_MODELED_YEAR, and ``Parameter.update`` never removes
            # values dated before the period it sets, so they keep it.
            self.parameters = backdate_parameters(
                self.parameters, first_instant=f"{FIRST_MODELED_YEAR}-01-01"
            )

        structural_reform = create_structural_reforms_from_parameters(
            self.parameters, start_instant
        )
        if reform is None:
            reform = ()
        reform = (reform, structural_reform)

        for parameter in self.parameters.get_descendants():
            parameter.modified = False

        if reform is not None:
            self.apply_reform_set(reform)

        self.add_variables(*create_50_state_variables())

        # Last, so reforms to a national total or to the population series
        # reach the per-capita series the variables uprate by.
        add_per_capita_uprating(self)
        self._per_capita_uprating_built = True

    def can_derive_reform_systems(self) -> bool:
        """Whether ``derive_reform_system`` gives what a full rebuild would.

        Only a system built without a reform, and changed in neither its
        variable registry nor its parameters since, holds the policy that
        construction reaches before it applies a reform. A clone drops the
        record of the build (``clone_spm_system``); a shallow copy that still
        reads the same registry objects and tree keeps it, and derives the
        same system. A subclass with its own constructor may build more than
        ``_apply_reforms`` gives a derived system, so it is rebuilt.

        The check sees every change to the variable registry, and every
        parameter change made through ``Parameter.update``, which marks the
        parameter and its ancestors modified; reform dictionaries and most
        ``modify_parameters`` modifiers change parameters that way. It does
        not see changes that mark nothing: nodes added or replaced with
        ``add_child``, ``_replace_child`` or ``merge`` (by a modifier, or by
        ``load_extension`` for an extension's parameters), assignments to
        ``values_list[i].value``, and edits to metadata or to a variable's
        attributes. A reform system derived afterwards includes
        such changes, as every simulation that shares this system's policy
        already does; a full rebuild would not. Detecting them would need a
        comparison of the whole tree on every derivation (measured at 0.7 to
        1.6 s, against about 2.75 s for the derivation). The exception is the
        few nodes derivation itself undoes the per-capita step on: if a series
        the build added or refreshed, or the set of children of a node holding
        a refreshed one, has changed, the system is rebuilt.
        """
        build = self.__dict__.get("_unreformed_build")
        if build is None:
            return False
        if type(self).__init__ is not CountryTaxBenefitSystem.__init__:
            return False
        if self.variables.keys() != build.variables.keys() or any(
            self.variables[name] is not variable
            for name, variable in build.variables.items()
        ):
            return False
        # Derivation removes the per-capita series the build added and
        # restores those it refreshed, so those nodes must be as it left them.
        if not per_capita_nodes_unchanged(
            self.parameters,
            build.per_capita_series_added | build.per_capita_series_replaced.keys(),
            build.per_capita_parent_children,
        ):
            return False
        # Construction leaves every parameter unmodified, and
        # ``Parameter.update`` marks what it changes. A node added after
        # construction has no flag at all: an unmarked change, like those
        # the docstring lists.
        return not any(
            getattr(parameter, "modified", False)
            for parameter in self.parameters.get_descendants()
        )

    def derive_reform_system(
        self,
        reform,
        start_instant: Annotated[
            str, "ISO date format YYYY-MM-DD"
        ] = DEFAULT_START_DATE,
        spm: dict | None = None,
    ) -> "CountryTaxBenefitSystem":
        """The system ``CountryTaxBenefitSystem(reform, start_instant, spm)``
        builds, without loading or processing any parameter or variable file.

        Construction loads about 12,000 parameter files and 12,300 variable
        files and then homogenizes, interpolates, uprates and backdates the
        tree, none of which depends on the reform. So copy this system's
        processed parameters and its variable registry from before the
        structural reforms, and run only the steps that follow
        (``_apply_reforms``): apply the reform, detect the structural reforms
        from the reformed parameters at ``start_instant``, add the per-state
        variables and rebuild the per-capita uprating series.

        Like core's ``Reform(baseline)``, this clones the parameter tree and
        copies the variable dictionary, but the result is a
        ``CountryTaxBenefitSystem``. A core ``Reform`` takes its class
        attributes and methods from ``TaxBenefitSystem`` instead, which drops
        ``auto_carry_over_input_variables`` and this class's ``clone`` and
        ``modify_parameters``.

        Variable objects are shared with this system, as ``share_spm_policy``
        shares them with every ordinary simulation: each core operation a
        reform performs on a variable binds a new object to the name. The
        exceptions are the variables that uprate by a national total, which
        the per-capita step changes in place: those are fresh copies of the
        recorded ones.

        Edits written directly into this system's objects, bypassing the
        methods that mark parameters modified, carry over into the derived
        system (see ``can_derive_reform_systems``).
        """
        if not self.can_derive_reform_systems():
            raise ValueError(
                "Only a system built without a reform, and unchanged since, "
                "can derive reform systems; build CountryTaxBenefitSystem("
                "reform=...) instead."
            )
        derived = plain_policy_copy(self)
        derived._unreformed_build = None
        # A simulation may have bound this system as its own; the derived
        # system is not bound to any simulation yet.
        derived.__dict__.pop("simulation", None)
        # Core's clone copies the root node's attributes, including the mark
        # that another system reads this tree and any tracer a traced request
        # wrote there. A tree loaded from files has no mark (which reads as
        # unshared) and no tracer.
        build = self._unreformed_build
        parameters = self.parameters.clone()
        parameters.__dict__.pop(SHARED_TREE_MARK, None)
        parameters.trace = False
        parameters.tracer = None
        parameters.branch_name = None
        # In the default build, the per-capita step that ends construction is
        # the only step after the recorded point that changes the tree: it
        # adds series and refreshes some that parameter uprating built. Undo
        # both, so a reform sees the series a full rebuild has when it
        # applies the reform.
        for path in build.per_capita_series_added:
            remove_per_capita_series(parameters, path)
        for path, earlier in build.per_capita_series_replaced.items():
            restore_per_capita_series(parameters, path, detached_copy(earlier))
        for parent_path, order in build.per_capita_parent_child_order.items():
            restore_child_order(parameters, parent_path, order)
        derived.parameters = parameters
        derived._parameters_at_instant_cache = {}
        derived.variables = dict(build.variables_before_reforms)
        # Fresh copies each time: the per-capita step points them at the
        # per-capita series in place, and a reform's ``update_variable``
        # inherits the national total from them as it does in a full rebuild.
        derived.variables.update(
            (name, variable.clone())
            for name, variable in build.total_uprated_variables.items()
        )
        bind_private_entities(derived)
        derived.spm_forecast_provider = create_spm_provider(spm)
        derived.modelled_policies = deepcopy(self.modelled_policies)
        derived.variable_module_metadata = dict(self.variable_module_metadata)
        # Construction applies the reform before it builds the per-capita
        # series, so ``modify_parameters`` must not rebuild them midway.
        derived._per_capita_uprating_built = False
        derived._apply_reforms(reform, start_instant)
        return derived

    def modify_parameters(self, modifier_function):
        result = super().modify_parameters(modifier_function)
        # Reforms applied after init (core's Simulation applies the reform
        # once more) must reach the derived per-capita series too.
        if getattr(self, "_per_capita_uprating_built", False):
            add_per_capita_uprating(self)
        return result

    def clone(self):
        return clone_spm_system(self)


system = CountryTaxBenefitSystem()


def _move_inputs_to_pre_response_variables(simulation):
    """Store aggregate inputs on the pre-response variables they derive from."""
    for aggregate, pre_response in PRE_RESPONSE_INPUTS.items():
        holder = simulation.get_holder(aggregate)
        for known_period in holder.get_known_periods():
            array = holder.get_array(known_period)
            simulation.set_input(pre_response, known_period, array)
            delete_input_values(holder, known_period)


def _sync_input_variables(simulation):
    """List the variables that hold inputs after the moves and backfill.

    Core records ``input_variables`` before the pre-response moves and the
    ``state_code`` backfill run, so the recorded list still names the emptied
    aggregates and ``state_code_str`` and omits the variables that now hold
    their values. Branch-based variables such as ``marginal_tax_rate`` delete
    every variable outside this list, so a stale list erases those inputs in
    the branch: a wage-earning parent's TANF then counts no earnings.
    """
    moved = (
        *PRE_RESPONSE_INPUTS,
        *PRE_RESPONSE_INPUTS.values(),
        "state_code_str",
        "state_code",
    )

    def holds_input(variable):
        return len(simulation.get_holder(variable).get_known_periods()) > 0

    input_variables = [
        variable
        for variable in simulation.input_variables
        if variable not in moved or holds_input(variable)
    ]
    simulation.input_variables = input_variables + [
        variable
        for variable in moved
        if variable not in input_variables and holds_input(variable)
    ]


def _rebuild_baseline_branch(simulation):
    """Branch a reformed simulation's baseline again, after the moves.

    Core branches the baseline while it constructs a reformed simulation,
    before the wrappers move inputs and backfill ``state_code``. The branch
    therefore kept ``employment_income`` and ``weekly_hours_worked`` as
    inputs, left ``employment_income_before_lsr`` and
    ``weekly_hours_worked_before_lsr`` empty, and kept the stale
    ``input_variables``. Its TANF counted no earnings, and the baseline
    marginal tax rate that labor supply responses compare against erased
    pre-response wages. Branching again from the simulation, as core's
    ``subsample`` does, gives the baseline the same inputs as the reform.
    """
    baseline = simulation.branches.pop("baseline", None)
    if baseline is None:
        return
    # A branch copies its parent's attributes, and a baseline whose own
    # baseline is set would compute behavioral responses.
    simulation.baseline = None
    rebuilt = simulation.get_branch("baseline")
    rebuilt.trace = simulation.trace
    rebuilt.tracer = simulation.tracer
    rebuilt.tax_benefit_system = baseline.tax_benefit_system
    # Cloning bound holders to reform variables. Restoring policy must also
    # restore those bindings and remove inputs that exist only in the reform.
    rebuilt._rebind_holders()
    rebuilt._isolate_parameter_tracing()
    simulation.baseline = rebuilt


def _backfill_state_code_from_str(simulation):
    """Backfill the ``state_code`` enum from a ``state_code_str`` input.

    The geography variables derive one-directionally
    (``state_fips`` -> ``state_name`` -> ``state_code`` -> ``state_code_str``),
    so a situation that sets only ``state_code_str`` feeds no upstream reader:
    every variable that reads the ``state_code`` enum silently falls back to
    its default (``StateCode.CA``) while ``state_code_str`` readers see the
    intended state (PolicyEngine/policyengine-us#8887).

    Mirror the ``employment_income`` -> ``employment_income_before_lsr`` moves
    above: when ``state_code`` has no known periods but ``state_code_str``
    does, encode the strings into ``state_code`` and drop the
    ``state_code_str`` arrays so derivation is canonical (``state_code_str``
    re-derives from ``state_code``). An explicitly set ``state_code`` always
    wins, and datasets are unaffected because they carry ``state_fips`` rather
    than ``state_code_str``.
    """
    state_code = simulation.get_holder("state_code")
    if state_code.get_known_periods():
        # An explicit state_code (e.g. from a dataset or situation) wins.
        return
    state_code_str = simulation.get_holder("state_code_str")
    for known_period in state_code_str.get_known_periods():
        array = state_code_str.get_array(known_period)
        simulation.set_input("state_code", known_period, StateCode.encode(array))
        state_code_str.delete_arrays(known_period)


class Simulation(TobCalculationMixin, SPMSimulationMixin, CoreSimulation):
    """
    A simulation of the tax-benefit system for the United States,
    defined against the base simulation class in the -core package.

    This simulation is commonly used for household-level impacts, as it
    does not include society-wide microdata.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The first
        date checked when deciding which structural reforms apply; defaults
        to 2024-01-01. Most structural reforms are checked on January 1 of
        ten consecutive years from this date, and some only on this date, so
        set it when a reform's parameter turns on outside those dates.
    """

    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR

    def __init__(self, *args, **kwargs):
        start_instant: Annotated[str, "ISO date format YYYY-MM-DD"] = kwargs.pop(
            "start_instant", DEFAULT_START_DATE
        )
        args, kwargs = self._prepare_spm_system(
            args, kwargs, kwargs.pop("spm", None), start_instant
        )
        validate_section_911_batch_inputs(
            kwargs.get("situation"),
            kwargs.get("default_input_period") or self.default_input_period,
        )
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, start_instant
        )
        if reform is not None:
            self.apply_reform(reform)

        migrate_social_security_inputs(self)
        _move_inputs_to_pre_response_variables(self)
        # Geography backfill: state_code_str-only input -> state_code enum.
        _backfill_state_code_from_str(self)
        _sync_input_variables(self)
        _rebuild_baseline_branch(self)


def _download_or_explain(dataset_str, download):
    """Name the unresolved dataset URI instead of re-raising a Hub exception.

    A build id that is not published yet, a renamed repository and an offline
    cache miss all surface from ``huggingface_hub`` as transport-level errors
    that never mention which dataset the model was asked for.
    """
    from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError

    try:
        return download()
    except (HfHubHTTPError, LocalEntryNotFoundError) as error:
        raise FileNotFoundError(
            f"Could not resolve the dataset {dataset_str!r}: {error}. "
            "Check that the build id in the URI is published, or pass a "
            "dataset= argument that is."
        ) from error


def _resolve_dataset_path(dataset_str):
    """Resolve a dataset string to a local file path, downloading if needed."""
    if dataset_str.startswith("hf://datasets/"):
        # Hugging Face *dataset* repos (e.g. Microcosm). `download_huggingface_dataset`
        # assumes a model repo, so resolve dataset repos directly. URL form:
        # hf://datasets/<owner>/<repo>/<path/to/file>[@<revision>]
        from huggingface_hub import hf_hub_download

        remainder = dataset_str[len("hf://datasets/") :]
        owner, repo, *file_parts = remainder.split("/")
        repo_filename = "/".join(file_parts)
        version = None
        if "@" in repo_filename:
            repo_filename, version = repo_filename.rsplit("@", 1)
        return _download_or_explain(
            dataset_str,
            lambda: hf_hub_download(
                repo_id=f"{owner}/{repo}",
                filename=repo_filename,
                repo_type="dataset",
                revision=version,
            ),
        )
    if "hf://" in dataset_str:
        from policyengine_core.tools.hugging_face import (
            parse_hf_url,
            download_huggingface_dataset,
        )

        owner, repo, filename, version = parse_hf_url(dataset_str)
        return _download_or_explain(
            dataset_str,
            lambda: download_huggingface_dataset(
                repo=f"{owner}/{repo}",
                repo_filename=filename,
                version=version,
            ),
        )
    elif Path(dataset_str).exists():
        return dataset_str
    else:
        raise FileNotFoundError(f"Dataset file not found: {dataset_str}")


def _file_sha256(file_path):
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=None)
def _checked_default_dataset_digest(file_path, size, mtime_ns):
    """Digest the resolved default build once per process.

    The certified build is ~830 MB, so a per-construction digest would add
    about a third of a second to every default `Microsimulation`. Key the
    digest on the resolved path together with its size and modification time,
    so a replaced or re-downloaded cache entry is digested again rather than
    inheriting the previous file's verdict.
    """
    return _file_sha256(file_path)


def _verify_default_dataset(file_path):
    """Reject a default build whose bytes are not the certified ones."""
    stat = Path(file_path).stat()
    actual = _checked_default_dataset_digest(
        str(file_path), stat.st_size, stat.st_mtime_ns
    )
    if actual != DEFAULT_DATASET_SHA256:
        raise ValueError(
            f"The default dataset {DEFAULT_DATASET} resolved to {file_path}, "
            f"whose content is not the certified build: expected sha256 "
            f"{DEFAULT_DATASET_SHA256}, got {actual}. The build id in the "
            "default URI points at different bytes than this model version "
            "was certified against; upgrade policyengine-us, or pass an "
            "explicit dataset= argument to use that artifact deliberately."
        )


def _is_hdfstore_format(file_path):
    """Check if an HDF5 file uses entity-level HDFStore format.

    Entity-level files have top-level keys like 'person', 'household', etc.
    Variable-centric h5py files have variable names as top-level keys.
    """
    import pandas as pd

    entity_names = set(US_ENTITIES)
    try:
        with pd.HDFStore(file_path, mode="r") as store:
            keys = {k.strip("/").split("/")[0] for k in store.keys()}
            return bool(entity_names & keys)
    except (OSError, IOError, KeyError, ValueError):
        return False


class Microsimulation(TobCalculationMixin, SPMSimulationMixin, CoreMicrosimulation):
    """
    A microsimulation of the tax-benefit system for the United States,
    defined against the base microsimulation class in the -core package.

    This simulation contains society-wide representative microdata, and is
    thus suitable for society-level impacts.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The first
        date checked when deciding which structural reforms apply; defaults
        to 2024-01-01. Most structural reforms are checked on January 1 of
        ten consecutive years from this date, and some only on this date, so
        set it when a reform's parameter turns on outside those dates.
        dataset_end_year(int | None): Optional; The final year to create when
        automatically extending an entity-level single-year dataset. Defaults
        to the latest supported economic-assumption year. This option applies
        only to the default dataset, entity-level HDFStore paths, and
        USSingleYearDataset instances.
    """

    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = DEFAULT_DATASET
    # Microdata stays in its base year: core labels a dataset without its own
    # year with the default input period, and values are not uprated for it.
    default_dataset_year = _DEFAULT_TIME_PERIOD
    default_role = "member"
    default_calculation_period = _DEFAULT_TIME_PERIOD
    default_input_period = _DEFAULT_TIME_PERIOD

    def __init__(self, *args, **kwargs):
        start_instant: Annotated[str, "ISO date format YYYY-MM-DD"] = kwargs.pop(
            "start_instant", DEFAULT_START_DATE
        )
        dataset_end_year: int | None = kwargs.pop("dataset_end_year", None)
        args, kwargs = self._prepare_spm_system(
            args, kwargs, kwargs.pop("spm", None), start_instant
        )

        dataset = kwargs.get("dataset")
        # Only the build this model version chose for itself is content-checked
        # below; a caller-supplied dataset= is the caller's own artifact.
        uses_country_default = dataset is None
        if dataset is None:
            # Route the class default through the same interception below as an
            # explicit dataset, so an entity-level (HDFStore) default such as
            # Microcosm is loaded via USSingleYearDataset rather than core's
            # variable-centric loader.
            dataset = self.default_dataset
            kwargs["dataset"] = dataset
        if dataset is not None and isinstance(dataset, str) and "cps_2023" in dataset:
            self.default_input_period = 2023

        # Dataset interception for entity-level HDFStore format.
        #
        # USSingleYearDataset and USMultiYearDataset duck-type the
        # policyengine-core Dataset interface (load(), data_format,
        # time_period, name) so that core's build_from_dataset() can
        # consume them.  Long-term, core should natively support
        # entity-level datasets, making this interception unnecessary.
        if dataset is not None and isinstance(dataset, str):
            local_path = _resolve_dataset_path(dataset)
            if uses_country_default and dataset == DEFAULT_DATASET:
                # A subclass may point `default_dataset` elsewhere; only the
                # shipped default is certified by DEFAULT_DATASET_SHA256.
                _verify_default_dataset(local_path)
            if _is_hdfstore_format(local_path):
                from policyengine_us.data.economic_assumptions import (
                    extend_single_year_dataset,
                )

                single = USSingleYearDataset(file_path=local_path)
                multi = extend_single_year_dataset(single, end_year=dataset_end_year)
                kwargs["dataset"] = multi
            elif dataset_end_year is not None:
                raise ValueError(
                    "dataset_end_year applies only to entity-level "
                    "single-year datasets."
                )
        elif isinstance(dataset, USSingleYearDataset):
            from policyengine_us.data.economic_assumptions import (
                extend_single_year_dataset,
            )

            multi = extend_single_year_dataset(dataset, end_year=dataset_end_year)
            kwargs["dataset"] = multi
        elif dataset_end_year is not None:
            raise ValueError(
                "dataset_end_year applies only to entity-level single-year datasets."
            )
        # USMultiYearDataset instances are already extended and pass
        # through to core unchanged.

        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, start_instant
        )
        if reform is not None:
            self.apply_reform(reform)

        migrate_social_security_inputs(self)
        _move_inputs_to_pre_response_variables(self)
        # Geography backfill: state_code_str-only input -> state_code enum.
        # Datasets carry state_fips, so this only fires for situations that
        # explicitly supply state_code_str.
        _backfill_state_code_from_str(self)
        _sync_input_variables(self)
        _rebuild_baseline_branch(self)


class IndividualSim(CoreIndividualSim):  # Deprecated
    tax_benefit_system = CountryTaxBenefitSystem
    entities = {entity.key: entity for entity in entities}
    default_dataset = DEFAULT_DATASET
    default_roles = dict(
        tax_unit="member",
        spm_unit="member",
        household="member",
        family="member",
    )
    required_entities = [
        "tax_unit",
        "spm_unit",
        "household",
        "family",
    ]
