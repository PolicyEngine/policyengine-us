from openfisca_us.microdata.utils import US, dataset
from openfisca_us.microdata.datasets.acs.raw_acs import RawACS
from pandas import DataFrame
import h5py


@dataset
class ACS:
    name = "acs"
    model = US

    # Note: no self because it uses a decorator.
    def generate(year: int) -> None:
        """Generates the ACS dataset.

        Args:
            year (int): The year of the raw ACS to use.
        """

        # Prepare raw ACS tables
        year = int(year)
        if year not in RawACS.years:
            RawACS.generate(year)

        raw_data = RawACS.load(year)
        acs = h5py.File(ACS.file(year), mode="w")

        person, spm_unit, household = [
            raw_data[entity] for entity in ("person", "spm_unit", "household")
        ]

        add_ID_variables(acs, person, spm_unit, household)
        add_SPM_variables(acs, spm_unit)

        raw_data.close()
        acs.close()


def add_ID_variables(
    acs: h5py.File,
    person: DataFrame,
    spm_unit: DataFrame,
    household: DataFrame,
):
    """Add basic ID and weight variables.

    Args:
        acs (h5py.File): The ACS dataset file.
        person (DataFrame): The person table of the ACS.
        spm_unit (DataFrame): The SPM unit table created from the person table
            of the ACS.
        household (DataFrame): The household table of the ACS.
    """
    # Add primary and foreign keys
    acs["person_id"] = person.SERIALNO * 1e2 + person.SPORDER
    acs["person_spm_unit_id"] = person.SPM_ID
    acs["spm_unit_id"] = spm_unit.SPM_ID
    # ACS doesn't have tax units.
    acs["tax_unit_id"] = spm_unit.SPM_ID
    # Until we add a family table, we'll use the person table.
    acs["family_id"] = spm_unit.SPM_ID
    acs["person_household_id"] = person.SERIALNO
    acs["person_tax_unit_id"] = person.SPM_ID
    acs["person_family_id"] = person.SPM_ID
    acs["household_id"] = household.SERIALNO

    # Add weights
    acs["person_weight"] = person.WT


def add_SPM_variables(acs: h5py.File, spm_unit: DataFrame):
    acs["SPM_unit_net_income"] = spm_unit.SPM_RESOURCES
    acs["poverty_threshold"] = spm_unit.SPM_POVTHRESHOLD
