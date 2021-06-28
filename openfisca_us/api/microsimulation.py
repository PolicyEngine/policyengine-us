from microdf.generic import MicroDataFrame
import numpy as np
from openfisca_core import periods
from openfisca_core.model_api import *
import openfisca_us
import pandas as pd
from openfisca_core.simulation_builder import SimulationBuilder
from pathlib import Path
from microdf import MicroSeries

MICRODATA = Path(__file__).parent.parent / "microdata"

class Microsimulation:
    def __init__(self, *reforms):
        self.reforms = reforms
        self.load_cps()
        self.bonus_sims = {}

    def apply_reforms(self, reforms: list) -> None:
        """Applies a list of reforms to the tax-benefit system.

        Args:
            reforms (list): A list of reforms. Each reform can also be a list of reforms.
        """
        for reform in reforms:
            if isinstance(reform, tuple) or isinstance(reform, list):
                self.apply_reforms(reform)
            else:
                self.system = reform(self.system)

    def load_cps(self):
        self.system = openfisca_us.CountryTaxBenefitSystem()
        self.apply_reforms(self.reforms)
        builder = SimulationBuilder()
        builder.create_entities(self.system)

        cps = pd.read_csv(MICRODATA / "cps.csv")
        weight_file = pd.read_csv(MICRODATA / "cps_weights.csv")

        self.weights = {}
        for column in weight_file:
            year = int(column[2:])
            self.weights[year] = weight_file[column].values * 1e-2

        indices = np.arange(len(cps))
        taxunits = builder.declare_entity("taxunit", indices)
        persons = builder.declare_person_entity("person", indices)
        builder.join_with_persons(taxunits, indices, np.array(["head"] * len(cps)))

        model = builder.build(self.system)
        input_periods = [periods.period(year) for year in range(2016, 2030)]

        for column in cps.columns:
            if column in self.system.variables:
                for input_period in input_periods:
                    model.set_input(column, input_period, cps[column].values)

        self.simulation = model

    def calc(self, variable, year=2019):
        values = self.simulation.calculate(variable, periods.period(year))
        series = MicroSeries(values, weights=self.weights[year])
        return series
    
    def df(self, variables, year=2019):
        df_dict = {}
        for var in variables:
            df_dict[var] = self.calc(var, year=year)
        return MicroDataFrame(df_dict, weights=self.weights[year])
    
    def deriv(
        self,
        target="tax",
        wrt="employment_income",
        delta=100,
        percent=False,
        group_limit=2,
    ) -> MicroSeries:
        """Calculates effective marginal tax rates over a population.

        Args:
            targets (str, optional): The name of the variable to measure the derivative of. Defaults to "household_net_income".
            wrt (str, optional): The name of the independent variable. Defaults to "employment_income".

        Returns:
            np.array: [description]
        """
        system = self.simulation.tax_benefit_system
        target_entity = system.variables[target].entity.key
        wrt_entity = system.variables[wrt].entity.key
        if target_entity == wrt_entity:
            # calculating a derivative with both source and target in the same entity
            config = (wrt, delta, percent, "same-entity")
            if config not in self.bonus_sims:
                existing_var_class = system.variables[wrt].__class__

                altered_variable = type(wrt, (existing_var_class,), {})
                if not percent:
                    altered_variable.formula = (
                        lambda *args: existing_var_class.formula(*args) + delta
                    )
                else:
                    altered_variable.formula = (
                        lambda *args: existing_var_class.formula(*args)
                        * (1.0 + delta / 100)
                    )

                class bonus_ref(Reform):
                    def apply(self):
                        self.update_variable(altered_variable)

                self.bonus_sims[config] = Microsimulation(
                    self.reforms[1:] + (bonus_ref,),
                )
            bonus_sim = self.bonus_sims[config]
            bonus_increase = bonus_sim.calc(wrt).astype(float) - self.calc(
                wrt
            ).astype(float)
            target_increase = bonus_sim.calc(target).astype(float) - self.calc(
                target
            ).astype(float)

            gradient = target_increase / bonus_increase

            return gradient
        elif (
            target_entity in ("taxunit",)
            and wrt_entity == "person"
        ):
            # calculate the derivative for a group variable wrt a source variable, independent of other members in the group
            adult = True
            index_in_group = (
                self.calc("person_id")
                .groupby(self.calc(f"{target_entity}_id", map_to="person"))
                .cumcount()
            )
            max_group_size = min(max(index_in_group[adult]) + 1, group_limit)

            derivative = np.empty((len(adult))) * np.nan

            for i in range(
                max_group_size, desc="Calculating independent derivatives"
            ):
                config = (wrt, delta, percent, "group-entity", i)
                if config not in self.bonus_sims:
                    existing_var_class = system.variables[wrt].__class__

                    altered_variable = type(wrt, (existing_var_class,), {})
                    if not percent:
                        altered_variable.formula = (
                            lambda person, *args: existing_var_class.formula(
                                person, *args
                            )
                            + delta * (index_in_group == i) * adult
                        )
                    else:
                        delta /= 100
                        altered_variable.formula = (
                            lambda *args: existing_var_class.formula(*args)
                            * (1.0 + delta * (index_in_group == i) * adult)
                        )

                    class bonus_ref(Reform):
                        def apply(self):
                            self.update_variable(altered_variable)

                    self.bonus_sims[config] = Microsimulation(
                        self.reforms[1:] + (bonus_ref,),
                        mode=self.mode,
                        year=self.year,
                        input_year=self.input_year,
                    )
                bonus_sim = self.bonus_sims[config]
                bonus_increase = bonus_sim.calc(wrt).astype(float) - self.calc(
                    wrt
                ).astype(float)
                target_increase = bonus_sim.calc(
                    target, map_to="person"
                ).astype(float) - self.calc(target, map_to="person").astype(
                    float
                )
                result = target_increase / bonus_increase
                derivative[bonus_increase > 0] = result[bonus_increase > 0]

            return MicroSeries(
                derivative, weights=self.entity_weights["person"]
            )
        else:
            raise ValueError(
                "Unable to compute derivative - target variable must be from a group of or the same as the source variable"
            )