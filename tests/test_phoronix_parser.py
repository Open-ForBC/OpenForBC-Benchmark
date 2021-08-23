import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from common.phoronix_parser import (clone_dir, # noqa: E402
                                    o4bc_benchmark_dir,
                                    phoronix_init,
                                    phoronix_list,
                                    phoronix_exists,
                                    phoronix_install)


class TestPhoronixParser(unittest.TestCase):
    def test_init(self):
        phoronix_init()
        self.assertTrue(os.path.isdir(clone_dir))

    def test_list(self):
        phoronix_init()
        phoronix_list("")
        phoronix_list("vpxenc")
        self.assertRaises(Exception, phoronix_list, "doesnt_exists")

    def test_exists(self):
        phoronix_init()
        self.assertTrue(phoronix_exists("x11perf"))
        self.assertTrue(phoronix_exists("php", "1.0.0"))
        self.assertFalse(phoronix_exists("php", "5.5.5.5"))
        self.assertRaises(Exception, phoronix_exists, "doesnt_exists")
        self.assertRaises(Exception, phoronix_exists, "doesnt_exists", "1.0.0")

    def test_install(self):
        phoronix_init()
        target_astcenc_dir = os.path.join(o4bc_benchmark_dir, "phoronix-astcenc-1.1.0")
        phoronix_install("astcenc", "1.1.0")
        self.assertTrue(os.path.isdir(target_astcenc_dir))
        self.assertTrue(os.path.isdir(os.path.join(target_astcenc_dir, "settings")))
        self.assertTrue(os.path.isfile(os.path.join(target_astcenc_dir, "benchmark_info.json")))
        self.assertTrue(os.path.isfile(os.path.join(target_astcenc_dir, "implementation.py")))
        self.assertRaises(Exception, phoronix_install, "doesnt_exists")
        self.assertRaises(Exception, phoronix_install, "doesnt_exists", "1.0.0")


if __name__ == "__main__":
    unittest.main()
