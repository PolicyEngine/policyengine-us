from time import time
from pathlib import Path
from typing import Callable, Dict, List, Tuple
from taxcalc import Calculator, Policy, Records
from openfisca_us.tools.dev.calcfunctions import *
from openfisca_us.system import CountryTaxBenefitSystem
import pandas as pd
import ast
import yaml
import argparse

np.random.seed(int(time()))
variables = CountryTaxBenefitSystem().variables

def extract_return(fname):
    for x in ast.walk(
        ast.parse(open(Path(__file__).parent / "calcfunctions.py").read())
    ):
        if not (isinstance(x, ast.FunctionDef)):
            continue
        if not (x.name == fname):
            continue
        for b in x.body:
            if isinstance(b, ast.Return):
                if isinstance(b.value, ast.Name):
                    yield b.value.id
                elif isinstance(b.value, ast.Tuple):
                    yield from [element.id for element in b.value.elts]


def get_inputs(fn: Callable) -> Tuple:
    """
    Return the inputs of a function.
    """
    return fn.__code__.co_varnames[: fn.__code__.co_argcount]


def get_outputs(fn: Callable) -> Tuple:
    """
    Return the outputs of a function.
    """
    return list(extract_return(fn.__name__))


policy = Policy()
TEST_YEAR = 2019
DEBUG_MODE = False
TAXCALC_CPS_CSV_FILE = "~/PSLmodels/Tax-Calculator/cps.csv"
cps = pd.read_csv(TAXCALC_CPS_CSV_FILE, nrows=1 if DEBUG_MODE else None)
policy.set_year(TEST_YEAR)

def safe_cast(x, t):
    try:
        return t(x)
    except:
        return x


def generate_input_values(
    inputs: List[str], output_names: List[str], overrides: Dict[str, float]
) -> Dict[str, float]:
    """Fetches the parameter value if the input is a parameter,
    otherwise returns the value from a random CPS tax unit.

    Args:
        inputs (List[str]): The input names.
        output_names (List[str]): The names of the outputs.
        overrides (Dict[str, float]): A dictionary of overrides.

    Returns:
        Dict[str, float]: The generated values.
    """
    if not DEBUG_MODE:
        try:
            cps_tax_unit = cps[(cps[output_names] != 0).min(axis=1)].sample(
                n=1
            )
        except:
            cps_tax_unit = cps.sample(n=1)
    result = {}
    for input_ in inputs:
        try:
            result[input_] = getattr(policy, input_)[0]
        except AttributeError:
            if input_ in overrides:
                result[input_] = overrides[input_]
            elif DEBUG_MODE:
                result[input_] = 0
            else:
                result[input_] = int(cps_tax_unit[input_].values[0])
    return result


def generate_unit_test(
    fn_name: str, input_overrides: Dict[str, float] = None
) -> Tuple[dict, Callable[[dict], Tuple[float]], Tuple[float]]:
    """Generates a unit test for a calcfunctions function.

    Args:
        fn_name (str): The name of the taxcalc function.
        input_overrides (Dict[str, float]): A dictionary of overrides.

    Returns:
        Tuple[dict, Callable[[dict, Tuple[float]]], Tuple[float]]: Keyword args, the function taking them and the expected result.
    """
    if input_overrides is None:
        input_overrides = {}
    fn = CALCFUNCTIONS[fn_name]

    def fn_(inputs):
        result = fn(**inputs)
        if not isinstance(result, tuple):
            result = (result,)
        return result

    kwargs = generate_input_values(
        get_inputs(fn), get_outputs(fn), overrides=input_overrides
    )

    return kwargs, fn_, fn_(kwargs)


def attempt_generate_all_nonzero_unit_test(
    fn_name: str,
) -> Tuple[dict, Callable[[dict], Tuple[float]], Tuple[float]]:
    for _ in range(1_000):
        kwargs, fn_, result = generate_unit_test(fn_name)
        # This function often needs manually modifying depending on the function
        if all([i != 0 for i in result]):
            return kwargs, fn_, result


def generate_yaml_test_dict(fn_name: str, name: str = None):
    kwargs, _, result = attempt_generate_all_nonzero_unit_test(fn_name)
    outputs = get_outputs(CALCFUNCTIONS[fn_name])
    input_dict = {
        rename_variable(x): safe_cast(translate_value(x, y), lambda x: round(float(x), 2))
        for x, y in kwargs.items()
        if x in cps and x not in outputs
    }
    structured_input_dict = convert_tc_structure_to_openfisca(input_dict)
    test_dict = dict(
        name=f"Unit test for {fn_name}" if name is None else name,
        period=2019,
        absolute_error_margin=0.01,
        input=structured_input_dict,
        tc_input=input_dict,
        output={
            rename_variable(name): float(res)
            for name, res in zip(outputs, result)
        },
    )
    return test_dict

def convert_tc_structure_to_openfisca(input_dict: dict) -> dict:
    new_input_dict = {"people": {}, "tax_units": {"tax_unit": {"members": []}}}
    if "n06" in input_dict and input_dict["n06"] > 0:
        for i in range(int(input_dict.get("n06"))):
            name = f"child_under_6_{i+1}"
            new_input_dict["people"][name] = {
                "age": 5,
                "is_tax_unit_dependent": True,
            }
            new_input_dict["tax_units"]["tax_unit"]["members"].append(name)
    if "n24" in input_dict and input_dict["n24"] - (input_dict.get("n06") or 0) > 0:
        for i in range(int(input_dict.get("n24") - (input_dict.get("n06") or 0))):
            name = f"child_under_17_over_6_{i+1}"
            new_input_dict["people"][name] = {
                "age": 16,
                "is_tax_unit_dependent": True,
            }
            new_input_dict["tax_units"]["tax_unit"]["members"].append(name)
    if "XTOT" in input_dict and "n24" in input_dict and "n1820" in input_dict:
        num_young_adult_dependents = min(input_dict["n1820"], input_dict["XTOT"] - input_dict["n24"])
        for i in range(int(num_young_adult_dependents)):
            name = f"young_adult_dependent_{i+1}"
            new_input_dict["people"][name] = {
                "age": 16,
                "is_tax_unit_dependent": True,
            }
            new_input_dict["tax_units"]["tax_unit"]["members"].append(name)
        if "n21" in input_dict:
            num_older_dependents = min(input_dict["n21"], input_dict["XTOT"] - input_dict["n24"] - num_young_adult_dependents)
            for i in range(int(num_older_dependents)):
                name = f"older_dependent_{i+1}"
                new_input_dict["people"][name] = {
                    "age": 21,
                    "is_tax_unit_dependent": True,
                }
                new_input_dict["tax_units"]["tax_unit"]["members"].append(name)
    if "num" in input_dict:
        if input_dict["num"] > 0:
            new_input_dict["people"]["primary"] = {
                "age": 18,
                "is_tax_unit_dependent": False,
            }
        if input_dict["num"] > 1:
            new_input_dict["people"]["spouse"] = {
                "age": 18,
                "is_tax_unit_dependent": False,
            }
    for key in input_dict:
        if key not in ("n06", "n24", "n1820", "n21", "XTOT", "num"):
            if key[-2:] == "_s" and "spouse" in input_dict["people"]:
                new_input_dict["people"]["spouse"][key:-1] = input_dict[key]
            elif key[-2:] == "_p" and "primary" in input_dict["people"]:
                new_input_dict["people"]["primary"][key[:-1]] = input_dict[key]
            elif variables[key].entity.key == "person":
                new_input_dict["people"]["primary"][key] = input_dict[key]
            elif variables[key].entity.key == "tax_unit":
                new_input_dict["tax_units"]["tax_unit"][key] = input_dict[key]
    return new_input_dict


def generate_yaml_tests(fn_name: str, n: int = 10) -> str:
    return yaml.dump(
        [
            generate_yaml_test_dict(
                fn_name,
                name=f"{fn_name} unit test {i + 1} (from generate_taxcalc_unit_tests.py)",
            )
            for i in range(n)
        ],
        sort_keys=False,
    )


RENAMES = {
    "MARS": "mars",
    "XTOT": "xtot",
}

VALUE_RENAMES = {
    "MARS": {
        1: "SINGLE",
        2: "JOINT",
        3: "SEPARATE",
        4: "HOUSEHOLD_HEAD",
        5: "WIDOW",
    }
}

INVERSE_RENAMES = {y: x for x, y in RENAMES.items()}

INVERSE_VALUE_RENAMES = {
    x: {b: a for a, b in y.items()} for x, y in VALUE_RENAMES.items()
}


def rename_variable(x):
    return RENAMES.get(x, x)


def translate_value(name, x):
    return VALUE_RENAMES[name].get(x, x) if name in VALUE_RENAMES else x


def inverse_rename_variable(x):
    return INVERSE_RENAMES.get(x, x)


def inverse_translate_value(name, x):
    return (
        INVERSE_VALUE_RENAMES[name].get(x, x)
        if name in INVERSE_VALUE_RENAMES
        else x
    )


def debug_test_yaml(fn_name: str, file: str, i: int = 0):
    with open(file, "r") as f:
        tests = yaml.safe_load(f)
    test = tests[i]
    input_overrides = {
        inverse_rename_variable(x): inverse_translate_value(
            inverse_rename_variable(x), y
        )
        for x, y in test["tc_input"].items()
    }
    kwargs, fn_, _ = generate_unit_test(fn_name, input_overrides)
    fn_(kwargs)


def generate_taxcalc_cps_df():
    r = Records.cps_constructor()
    p = Policy(year=TEST_YEAR)
    c = Calculator(policy=p, records=r)
    df = c.dataframe(None, all_vars=True)
    df.to_csv("cps.csv")


if __name__ == "__main__":
    if not DEBUG_MODE:
        parser = argparse.ArgumentParser(
            description="Generate unit tests for calcfunctions."
        )
        parser.add_argument(
            "function",
            type=str,
            help="The name of the function to generate unit tests for.",
        )
        parser.add_argument(
            "--n",
            type=int,
            default=10,
            help="The number of unit tests to generate.",
        )
        args = parser.parse_args()
        print(generate_yaml_tests(args.function, args.n))
    else:
        # An example of debugging a unit test
        debug_test_yaml(
            "GainsTax",
            "openfisca_us/tests/policy/baseline/calcfunctions/gainstax.yaml",
            2,
        )
