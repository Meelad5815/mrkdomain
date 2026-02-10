import tempfile
import unittest
from pathlib import Path

from internal_naming import InternalNameService


class InternalNameServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Path(self.tmp.name) / "names.json"
        self.svc = InternalNameService(store_path=str(self.store))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_register_and_resolve_valid_name(self) -> None:
        self.svc.register("Shop.MRK", "https://apps.local/shop")
        self.assertEqual(self.svc.resolve("shop.mrk"), "https://apps.local/shop")

    def test_rejects_invalid_suffix(self) -> None:
        with self.assertRaises(ValueError):
            self.svc.register("shop.com", "https://apps.local/shop")

    def test_rejects_empty_target(self) -> None:
        with self.assertRaises(ValueError):
            self.svc.register("shop.mrk", "  ")


if __name__ == "__main__":
    unittest.main()
