from hydro_roll_core import libcore

cb = libcore


def main():
    rule_pack = "example_rule_pack"
    result = cb.process_rule_pack(rule_pack)
    print(result)
    print(cb.name)
    cb.name = "a"
    print(cb.name)


if __name__ == "__main__":
    main()