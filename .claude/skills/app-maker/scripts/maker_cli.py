#!/usr/bin/env python3
"""The App Maker's actions from a terminal — used by stage sessions (e.g. positioning promotes research).

    maker_cli.py promote research/<slug> app_N     # research becomes the app; its settings move with it
    maker_cli.py start <app> <stage> [--mock]      # what a Start button does
"""
import sys
import maker

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["promote"] and len(a) == 3:
        print(maker.promote(a[1], a[2]))
    elif a[:1] == ["start"] and len(a) >= 3:
        print(maker.start_stage(a[1], a[2], mock=True if "--mock" in a else None))
    else:
        raise SystemExit(__doc__)
