import yaml
import os

# Custom representer function to preserve underscores in integers and floats
def representer(dumper, data):
    # If the data is an integer or a float, write it with underscores
    if isinstance(data, (int, float)):
        return dumper.represent_scalar(
            "tag:yaml.org,2002:int", "{:,}".format(data).replace(",", "_")
        )
    # Otherwise, use the default representer
    return dumper.represent_data(data)


# Recursive function to process YAML files in a folder
def process_folder(folder):
    # Iterate over all files in the folder
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        # If the file is a YAML file
        if file.endswith(".yaml"):
            try:
                # Load the YAML file
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f)
                # Remove the name field from the metadata
                if "metadata" in data and "name" in data["metadata"]:
                    del data["metadata"]["name"]
                # Create a RoundTripDumper object with the custom representer function
                dumper = yaml.RoundTripDumper(
                    None, default_flow_style=False, default_style=None
                )
                dumper.add_representer(int, representer)
                dumper.add_representer(float, representer)
                # Save the modified data back to the YAML file
                with open(file_path, "w") as f:
                    yaml.dump(data, f, Dumper=dumper)
                print(f"Success: {file_path}")
            except ValueError:
                # Print an error message if a ValueError is raised
                print(f"Error: {file_path}")
                continue
        # If the file is a folder, recursively process it
        elif os.path.isdir(file_path):
            process_folder(file_path)


# Starting folder
folder = "."
process_folder(folder)
