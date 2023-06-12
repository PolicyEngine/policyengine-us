import logging
from policyengine_core.data import PublicDataset
import h5py
from policyengine_us.data.datasets.huduser.raw_acs import RawHUDUSER
from policyengine_us.data.storage import policyengine_us_MICRODATA_FOLDER
from pandas import DataFrame


class HUDUSER(PublicDataset):
    name = "huduser"
    is_openfisca_compatible = True
    label = "HUDUSER"
    folder_path = policyengine_us_MICRODATA_FOLDER

    def generate(self, year: int) -> None:
        """Generates the HUDUSER dataset.

        Args:
            year (int): The year of the raw HUDUSER to use.
        """

        # Prepare raw HUDUSER tables
        year = int(year)
        if year in self.years:
            self.remove(year)
        if year not in RawHUDUSER.years:
            RawHUDUSER.generate(year)

        raw_data = RawHUDUSER.load(year)
        huduser_data = h5py.File(HUDUSER.file(year), mode="w")

        huduser_raw = raw_data["huduser"]
        # Add primary and foreign keys

        huduser_raw.FIPS = huduser_raw.FIPS.astype(int)
        # person.SERIALNO = person.SERIALNO.astype(int)
        # person.SPORDER = person.SPORDER.astype(int)
        # person.SPM_ID = person.SPM_ID.astype(int)
        # spm_unit.SPM_ID = spm_unit.SPM_ID.astype(int)

        # logging.info(
        #     f"HUDUSER with a linked household {person.SERIALNO.isin(household.SERIALNO).mean():.1%}"
        # )
        # person = person[person.SERIALNO.isin(household.SERIALNO)]
        # logging.info(
        #     f"Households with a linked person {household.SERIALNO.isin(person.SERIALNO).mean():.1%}"
        # )
        # household = household[household.SERIALNO.isin(person.SERIALNO)]
        # logging.info(
        #     f"SPM units with a linked person {spm_unit.SPM_ID.isin(person.SPM_ID).mean():.1%}"
        # )
        # spm_unit = spm_unit[spm_unit.SPM_ID.isin(person.SPM_ID)]

        add_variables(huduser_data, huduser_raw)
        # add_person_variables(huduser_data, person)
        # add_spm_variables(huduser_data, spm_unit)
        # add_household_variables(huduser_data, household)

        raw_data.close()
        huduser_data.close()


HUDUSER = HUDUSER()


def add_variables(
    huduser_data: h5py.File,
    huduser_raw: DataFrame,
) -> None:
    """Add basic AMI and FMR variables.

    Args:
        huduser_data (h5py.File): The ami dataset file.
        huduser_raw (DataFrame): The table of the ami.
    """
    huduser_data["state_fips"] = huduser_raw.fips
    huduser_data["ami"] = huduser_raw.median2023
    huduser_data["hud_vli_1"] = huduser_raw.l50_1
    huduser_data["hud_vli_2"] = huduser_raw.l50_2
    huduser_data["hud_vli_3"] = huduser_raw.l50_3
    huduser_data["hud_vli_4"] = huduser_raw.l50_4
    huduser_data["hud_vli_5"] = huduser_raw.l50_5
    huduser_data["hud_vli_6"] = huduser_raw.l50_6
    huduser_data["hud_vli_7"] = huduser_raw.l50_7
    huduser_data["hud_vli_8"] = huduser_raw.l50_8
    huduser_data["hud_eli_1"] = huduser_raw.ELI_1
    huduser_data["hud_eli_2"] = huduser_raw.ELI_2
    huduser_data["hud_eli_3"] = huduser_raw.ELI_3
    huduser_data["hud_eli_4"] = huduser_raw.ELI_4
    huduser_data["hud_eli_5"] = huduser_raw.ELI_5
    huduser_data["hud_eli_6"] = huduser_raw.ELI_6
    huduser_data["hud_eli_7"] = huduser_raw.ELI_7
    huduser_data["hud_eli_8"] = huduser_raw.ELI_8
    huduser_data["hud_li_1"] = huduser_raw.l80_1
    huduser_data["hud_li_2"] = huduser_raw.l80_2
    huduser_data["hud_li_3"] = huduser_raw.l80_3
    huduser_data["hud_li_4"] = huduser_raw.l80_4
    huduser_data["hud_li_5"] = huduser_raw.l80_5
    huduser_data["hud_li_6"] = huduser_raw.l80_6
    huduser_data["hud_li_7"] = huduser_raw.l80_7
    huduser_data["hud_li_8"] = huduser_raw.l80_8
    # FMR data for bedrooms.
    huduser_data["hud_fmr_0"] = huduser_raw.fmr_0
    huduser_data["hud_fmr_1"] = huduser_raw.fmr_1
    huduser_data["hud_fmr_2"] = huduser_raw.fmr_2
    huduser_data["hud_fmr_3"] = huduser_raw.fmr_3
    huduser_data["hud_fmr_4"] = huduser_raw.fmr_4


# def add_person_variables(ami: h5py.File, person: DataFrame) -> None:
#     ami["age"] = person.AGEP
#     ami["employment_income"] = person.WAGP
#     ami["self_employment_income"] = person.SEMP
#     ami["total_income"] = person.PINCP


# def add_spm_variables(ami: h5py.File, spm_unit: DataFrame) -> None:
#     ami["spm_unit_net_income_reported"] = spm_unit.SPM_RESOURCES
#     ami["spm_unit_spm_threshold"] = spm_unit.SPM_POVTHRESHOLD


# def add_household_variables(ami: h5py.File, household: DataFrame) -> None:
#     ami["household_vehicles_owned"] = household.VEH
#     ami["state_fips"] = ami["household_state_fips"] = household.ST
