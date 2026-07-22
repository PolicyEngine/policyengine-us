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
from policyengine_us.tools.parameters import backdate_parameters
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
from policyengine_us.data.dataset_schema import (
    US_ENTITIES,
    USSingleYearDataset,
    USMultiYearDataset,
)

from typing import Annotated, Optional

COUNTRY_DIR = Path(__file__).parent

CURRENT_YEAR = 2024
DEFAULT_START_DATE = str(CURRENT_YEAR) + "-01-01"

# Certified Populace build (primary-source US microdata), pinned by build id.
# Populace ships from a Hugging Face *dataset* repo, hence the `hf://datasets/`
# prefix handled in `_resolve_dataset_path`.
DEFAULT_DATASET = "hf://datasets/policyengine/populace-us/populace_us_2024.h5@populace-us-2024-c86a631-6e1bcd0271a5-20260619T002242Z"


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
        reform: Optional[tuple] = None,
        start_instant: Annotated[
            str, "ISO date format YYYY-MM-DD"
        ] = DEFAULT_START_DATE,
    ):
        super().__init__(entities, reform=reform)
        self.load_parameters(COUNTRY_DIR / "parameters")
        self.add_abolition_parameters()
        self.parameters = set_irs_uprating_parameter(self.parameters)
        self.parameters = homogenize_parameter_structures(
            self.parameters, self.variables
        )
        self.parameters = propagate_parameter_metadata(self.parameters)
        self.parameters = interpolate_parameters(self.parameters)
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
            self.parameters, first_instant="2015-01-01"
        )

        for parameter in self.parameters.get_descendants():
            parameter.modified = False

        if reform is not None:
            self.apply_reform_set(reform)

        self.add_variables(*create_50_state_variables())


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


class Simulation(CoreSimulation):
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
        return hf_hub_download(
            repo_id=f"{owner}/{repo}",
            filename=repo_filename,
            repo_type="dataset",
            revision=version,
        )
    if "hf://" in dataset_str:
        from policyengine_core.tools.hugging_face import (
            parse_hf_url,
            download_huggingface_dataset,
        )

        owner, repo, filename, version = parse_hf_url(dataset_str)
        return download_huggingface_dataset(
            repo=f"{owner}/{repo}",
            repo_filename=filename,
            version=version,
        )
    elif Path(dataset_str).exists():
        return dataset_str
    else:
        raise FileNotFoundError(f"Dataset file not found: {dataset_str}")


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


class Microsimulation(CoreMicrosimulation):
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

        dataset = kwargs.get("dataset")
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
            if _is_hdfstore_format(local_path):
                from policyengine_us.data.economic_assumptions import (
                    extend_single_year_dataset,
                )

                single = USSingleYearDataset(file_path=local_path)
                multi = extend_single_year_dataset(single)
                kwargs["dataset"] = multi
        elif isinstance(dataset, USSingleYearDataset):
            from policyengine_us.data.economic_assumptions import (
                extend_single_year_dataset,
            )

            multi = extend_single_year_dataset(dataset)
            kwargs["dataset"] = multi
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
