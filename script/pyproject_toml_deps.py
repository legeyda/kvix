import toml

with open("pyproject.toml", "r") as f:
    for x in toml.load(f).get("project", {}).get("dependencies", []):
        print(x)
