import sys

from packaging.version import Version


def next_version(current, part):
    v = Version(current)
    if part == "major":
        return f"{v.major + 1}.0.0"
    elif part == "minor":
        return f"{v.major}.{v.minor + 1}.0"
    elif part == "patch":
        return f"{v.major}.{v.minor}.{v.micro + 1}"
    else:
        raise ValueError("Specify 'major', 'minor', or 'patch'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python next_version.py <current_version> <major|minor|patch>")
        sys.exit(1)
    current_version = sys.argv[1]
    part = sys.argv[2]
    print(next_version(current_version, part))
