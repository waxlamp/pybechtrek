import sys
import yaml

import parser


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: gender.py <parsedlinefile> <genderdbfile> <genderedfile>", file=sys.stderr)
        return 1

    inputfile = sys.argv[1]
    genderdbfile = sys.argv[2]
    outputfile = sys.argv[3]

    with open(genderdbfile) as f:
        genderdb = yaml.safe_load(f)
        if genderdb is None:
            genderdb = {}

    with open(inputfile) as f:
        with open(outputfile, "w") as o:
            title = f.readline()
            print(title, file=o, end="")

            for text in f.readlines():
                line = parser.ParseObject.decode(text)

                if not isinstance(line, parser.Line):
                    print(text, file=o, end="")
                    continue

                if line.role.name == "UNKNOWN":
                    print(line.dialog)
                    name = input("Who spoke this line of dialog? ")

                    line.role.name = name.upper()

                gender = genderdb.get(line.role.name)
                if gender is None:
                    while gender not in ["m", "f", "u", "o"]:
                        response = input(f"What is {line.role.name}'s gender? ")
                        gender = response[0] if len(response) > 0 else None

                    save = None
                    while save not in ["y", "n"]:
                        response = input("Save in gender DB? ")
                        save = response[0] if len(response) > 0 else None

                    if save:
                        genderdb[line.role.name] = gender

                line.role.gender = gender

                print(line.encode(), file=o)

    with open(genderdbfile, "w") as f:
        yaml.safe_dump(genderdb, f)

if __name__ == "__main__":
    sys.exit(main())
