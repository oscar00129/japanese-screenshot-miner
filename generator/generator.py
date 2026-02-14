import os, stat

class Generator:
    @staticmethod
    def generate_config_file():
        filename = "config.toml"
        with open(filename, "w") as f:
            f.write("screenshot_folders = [\n\t\"\",\n]\n")
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)
        print("Config file generated. Please add a route of files.")