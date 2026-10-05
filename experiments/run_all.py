"""Run all experiments in order (single entrypoint for Docker verify)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import exp01_zins_verification as e1
import exp02_renten_tilgung as e2
import exp03_optimierung_benchmark as e3
import exp04_hidden_patterns as e4


def main():
    e1.main()
    e2.main()
    e3.main()
    e4.main()
    print("ALL_EXPERIMENTS_DONE")


if __name__ == "__main__":
    main()
