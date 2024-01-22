# -*- coding: utf-8 -*-

from pathlib_mate import Path

p1 = Path(__file__)
p2 = p1.joinpath("a")
p3 = p2.relative_to(p1)
p4 = p2 / "b"
p5 = p1.with_suffix(".txt")
p6 = p1.with_name("test.txt")

_ = p1.select()
_ = p2.select()
_ = p3.select()
_ = p4.select()
_ = p5.select()
_ = p6.select()

_ = Path.home().select()
_ = Path.cwd().select()
