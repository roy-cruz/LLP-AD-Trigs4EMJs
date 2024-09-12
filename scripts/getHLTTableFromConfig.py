import csv
import importlib.util
import argparse
import os
import tempfile

def extract_relevant_lines(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if 'process.schedule = cms.Schedule(' in line:
                break
            outfile.write(line)

def import_module_from_file(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main(config_file_path):
    temp_file_path = "temp_config.py"

    try:
        extract_relevant_lines(config_file_path, temp_file_path)

        # Get process object
        config_module = import_module_from_file(temp_file_path)
        process = config_module.process

        if process and hasattr(process, "PrescaleService"):
            labels = process.PrescaleService.lvl1Labels
            prescale_entries = process.PrescaleService.prescaleTable

            rows = []
            header = ["Name"] + [str(label) for label in labels]
            rows.append(header)

            for entry in prescale_entries:
                row = [entry.pathName.value()] + list(entry.prescales)
                rows.append(row)

            # Write to CSV
            csv_filename = "hlt_prescales.csv"
            with open(csv_filename, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(rows)

            print(f"CSV file '{csv_filename}' has been created.")
        else:
            print("PrescaleService not found in the provided configuration file.")
    
    finally:
        # Clean up
        os.remove(temp_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HLT prescale CSV from a config file.")
    parser.add_argument("config_path", type=str, help="Path to config file")

    args = parser.parse_args()
    main(args.config_path)