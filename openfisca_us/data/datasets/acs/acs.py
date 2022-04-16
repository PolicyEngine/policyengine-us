from openfisca_tools.data import PublicDataset
import h5py
from openfisca_us.data.datasets.acs.raw_acs import RawACS
from openfisca_us.data.storage import OPENFISCA_US_MICRODATA_FOLDER
from pandas import DataFrame


class ACS(PublicDataset):
    name = "acs"
    is_openfisca_compatible = True
    label = "ACS"
    folder_path = OPENFISCA_US_MICRODATA_FOLDER

    def generate(self, year: int) -> None:
        """Generates the ACS dataset.

        Args:
            year (int): The year of the raw ACS to use.
        """

        # Prepare raw ACS tables
        year = int(year)
        if year in self.years:
            self.remove(year)
        if year not in RawACS.years:
            RawACS.generate(year)

        raw_data = RawACS.load(year)
        acs = h5py.File(ACS.file(year), mode="w")

        person, spm_unit, household = [
            raw_data[entity] for entity in ("person", "spm_unit", "household")
        ]
        # Add primary and foreign keys

        def make_numeric(x):
            return int(x.replace("2019GQ", "0").replace("2019HU", "1"))

        household.SERIALNO = household.SERIALNO.apply(make_numeric)
        person.SERIALNO = person.SERIALNO.apply(make_numeric)

        person = person[person.SERIALNO.isin(household.SERIALNO)]
        household = household[household.SERIALNO.isin(person.SERIALNO)]
        spm_unit = spm_unit[spm_unit.SPM_ID.isin(person.SPM_ID)]

        add_id_variables(acs, person, spm_unit, household)
        add_spm_variables(acs, spm_unit)
        add_household_variables(acs, household)

        raw_data.close()
        acs.close()


ACS = ACS()


def add_id_variables(
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
    acs["person_weight"] = person.PWGTP
    acs["household_weight"] = household.WGTP


def add_spm_variables(acs: h5py.File, spm_unit: DataFrame):
    acs["spm_unit_net_income"] = spm_unit.SPM_RESOURCES
    acs["spm_unit_spm_threshold"] = spm_unit.SPM_POVTHRESHOLD


def add_household_variables(acs: h5py.File, household: DataFrame):
    acs["household_vehicles_owned"] = household.VEH
    acs["fips"] = household.ST
