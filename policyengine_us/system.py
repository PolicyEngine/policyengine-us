import hashlib
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
    FIRST_MODELED_YEAR,
    backdate_parameters,
)
from policyengine_us.reforms import create_structural_reforms_from_parameters
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
from .tools.per_capita_uprating import (
    add_per_capita_parameters_for_parameter_uprating,
    add_per_capita_uprating,
)
from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USSingleYearDataset,
    USMultiYearDataset,
)

from typing import Annotated
from spm_calculator.policyengine_adapter import build_policyengine_variables
from policyengine_us.spm import (
    SPMSimulationMixin,
    clone_spm_system,
    create_spm_provider,
)

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2024
DEFAULT_START_DATE = str(CURRENT_YEAR) + "-01-01"

# Certified Populace build (primary-source US microdata), pinned by build id.
# Populace ships from a Hugging Face *dataset* repo, hence the `hf://datasets/`
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


class CountryTaxBenefitSystem(TaxBenefitSystem):
    """
    The tax-benefit system for the United States.
    This structure is a modification of the -core
    package's base TaxBenefitSystem class.

    Args:
        reform (tuple | None): A tuple of reforms to apply to the system.
        If no reform is applied, the system will be initialized with the
        default tax/benefit parameters.

        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
    """

    variables_dir = COUNTRY_DIR / "variables"
    auto_carry_over_input_variables = True
    basic_inputs = [
        "state_name",
        "employment_income",
        "age",
    ]
    modelled_policies = COUNTRY_DIR / "programs.yaml"

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

        if reform:
            # Applied after the parameter processing pipeline so that values
            # a reform inserts at future dates cannot act as defined values
            # during uprating/interpolation, which would freeze the years
            # between the last legislated value and the reform start at the
            # last legislated nominal value (issue #9075) — and before
            # structural-reform detection, which reads reformed parameter
            # values.
            self.apply_reform_set(reform)

        structural_reform = create_structural_reforms_from_parameters(
            self.parameters, start_instant
        )
        if reform is None:
            reform = ()
        reform = (reform, structural_reform)

        self.parameters = backdate_parameters(
            self.parameters, first_instant=f"{FIRST_MODELED_YEAR}-01-01"
        )

        for parameter in self.parameters.get_descendants():
            parameter.modified = False

        if reform is not None:
            self.apply_reform_set(reform)

        self.add_variables(*create_50_state_variables())

        # Last, so reforms to a national total or to the population series
        # reach the per-capita series the variables uprate by.
        add_per_capita_uprating(self)
        self._per_capita_uprating_built = True

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


class Simulation(SPMSimulationMixin, CoreSimulation):
    """
    A simulation of the tax-benefit system for the United States,
    defined against the base simulation class in the -core package.

    This simulation is commonly used for household-level impacts, as it
    does not include society-wide microdata.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
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
        super().__init__(*args, **kwargs)

        reform = create_structural_reforms_from_parameters(
            self.tax_benefit_system.parameters, start_instant
        )
        if reform is not None:
            self.apply_reform(reform)

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in self_employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input("self_employment_income_before_lsr", known_period, array)
            self_employment_income.delete_arrays(known_period)

        sstb_self_employment_income = self.get_holder("sstb_self_employment_income")
        for known_period in sstb_self_employment_income.get_known_periods():
            array = sstb_self_employment_income.get_array(known_period)
            self.set_input(
                "sstb_self_employment_income_before_lsr", known_period, array
            )
            sstb_self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input("weekly_hours_worked_before_lsr", known_period, array)
            weekly_hours.delete_arrays(known_period)

        # Capital gains responses

        cg_holder = self.get_holder("long_term_capital_gains")
        for known_period in cg_holder.get_known_periods():
            array = cg_holder.get_array(known_period)
            self.set_input(
                "long_term_capital_gains_before_response", known_period, array
            )
            cg_holder.delete_arrays(known_period)

        # Geography backfill: state_code_str-only input -> state_code enum.
        _backfill_state_code_from_str(self)


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
        # Hugging Face *dataset* repos (e.g. Populace). `download_huggingface_dataset`
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


class Microsimulation(SPMSimulationMixin, CoreMicrosimulation):
    """
    A microsimulation of the tax-benefit system for the United States,
    defined against the base microsimulation class in the -core package.

    This simulation contains society-wide representative microdata, and is
    thus suitable for society-level impacts.

    Args:
        start_instant(str: ISO date format YYYY-MM-DD): Optional; The date
        at which the simulation begins; defaults to 2024-01-01; this is a
        temporary patch for structural reforms, and must be set to the start
        date of a structural reform parameter if it begins on a date other
        than the first day of the current year.
        dataset_end_year(int | None): Optional; The final year to create when
        automatically extending an entity-level single-year dataset. Defaults
        to the latest supported economic-assumption year. This option applies
        only to the default dataset, entity-level HDFStore paths, and
        USSingleYearDataset instances.
    """

    default_tax_benefit_system = CountryTaxBenefitSystem
    default_tax_benefit_system_instance = system
    default_dataset = DEFAULT_DATASET
    default_dataset_year = CURRENT_YEAR
    default_role = "member"
    default_calculation_period = CURRENT_YEAR
    default_input_period = CURRENT_YEAR

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
            # Populace is loaded via USSingleYearDataset rather than core's
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

        # Labor supply responses

        employment_income = self.get_holder("employment_income")
        for known_period in employment_income.get_known_periods():
            array = employment_income.get_array(known_period)
            self.set_input("employment_income_before_lsr", known_period, array)
            employment_income.delete_arrays(known_period)

        self_employment_income = self.get_holder("self_employment_income")
        for known_period in self_employment_income.get_known_periods():
            array = self_employment_income.get_array(known_period)
            self.set_input("self_employment_income_before_lsr", known_period, array)
            self_employment_income.delete_arrays(known_period)

        sstb_self_employment_income = self.get_holder("sstb_self_employment_income")
        for known_period in sstb_self_employment_income.get_known_periods():
            array = sstb_self_employment_income.get_array(known_period)
            self.set_input(
                "sstb_self_employment_income_before_lsr", known_period, array
            )
            sstb_self_employment_income.delete_arrays(known_period)

        weekly_hours = self.get_holder("weekly_hours_worked")
        for known_period in weekly_hours.get_known_periods():
            array = weekly_hours.get_array(known_period)
            self.set_input("weekly_hours_worked_before_lsr", known_period, array)
            weekly_hours.delete_arrays(known_period)

        # Capital gains responses

        cg_holder = self.get_holder("long_term_capital_gains")
        for known_period in cg_holder.get_known_periods():
            array = cg_holder.get_array(known_period)
            self.set_input(
                "long_term_capital_gains_before_response", known_period, array
            )
            cg_holder.delete_arrays(known_period)

        # Geography backfill: state_code_str-only input -> state_code enum.
        # Datasets carry state_fips, so this only fires for situations that
        # explicitly supply state_code_str.
        _backfill_state_code_from_str(self)

        self.input_variables = [
            variable
            for variable in self.input_variables
            if variable
            not in [
                "employment_income",
                "self_employment_income",
                "sstb_self_employment_income",
                "weekly_hours_worked",
                "capital_gains",
            ]
        ] + [
            "employment_income_before_lsr",
            "self_employment_income_before_lsr",
            "sstb_self_employment_income_before_lsr",
            "weekly_hours_worked_before_lsr",
            "long_term_capital_gains_before_response",
        ]


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
