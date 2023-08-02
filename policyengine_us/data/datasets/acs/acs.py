import logging
from policyengine_core.data import PublicDataset
import h5py
from policyengine_us.data.datasets.acs.raw_acs import RawACS
from policyengine_us.data.storage import policyengine_us_MICRODATA_FOLDER
from pandas import DataFrame


class ACS(PublicDataset):
    name = "acs"
    is_openfisca_compatible = True
    label = "ACS"
    folder_path = policyengine_us_MICRODATA_FOLDER

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

        household.SERIALNO = household.SERIALNO.astype(int)
        person.SERIALNO = person.SERIALNO.astype(int)
        person.SPORDER = person.SPORDER.astype(int)
        person.SPM_ID = person.SPM_ID.astype(int)
        spm_unit.SPM_ID = spm_unit.SPM_ID.astype(int)

        logging.info(
            f"Persons with a linked household {person.SERIALNO.isin(household.SERIALNO).mean():.1%}"
        )
        person = person[person.SERIALNO.isin(household.SERIALNO)]
        logging.info(
            f"Households with a linked person {household.SERIALNO.isin(person.SERIALNO).mean():.1%}"
        )
        household = household[household.SERIALNO.isin(person.SERIALNO)]
        logging.info(
            f"SPM units with a linked person {spm_unit.SPM_ID.isin(person.SPM_ID).mean():.1%}"
        )
        spm_unit = spm_unit[spm_unit.SPM_ID.isin(person.SPM_ID)]

        add_id_variables(acs, person, spm_unit, household)
        add_person_variables(acs, person)
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
) -> None:
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

    # TODO: add marital unit IDs - using person IDs for now
    acs["person_marital_unit_id"] = person.SERIALNO
    acs["marital_unit_id"] = person.SERIALNO.unique()

    # Add weights
    acs["person_weight"] = person.PWGTP
    acs["household_weight"] = household.WGTP


def add_person_variables(acs: h5py.File, person: DataFrame) -> None:
    acs["age"] = person.AGEP
    acs["employment_income"] = person.WAGP
    acs["self_employment_income"] = person.SEMP
    acs["total_income"] = person.PINCP


def add_spm_variables(acs: h5py.File, spm_unit: DataFrame) -> None:
    acs["spm_unit_net_income_reported"] = spm_unit.SPM_RESOURCES
    acs["spm_unit_spm_threshold"] = spm_unit.SPM_POVTHRESHOLD


def add_household_variables(acs: h5py.File, household: DataFrame) -> None:
    acs["household_vehicles_owned"] = household.VEH
    acs["state_fips"] = acs["household_state_fips"] = household.ST
