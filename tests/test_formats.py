import unittest
import os
import sys
from core.engine import OptimizationEngine

# Mocking paths for test environment if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMediaFormats(unittest.TestCase):
    def setUp(self):
        self.test_input = "test_dummy.mp4"
        # Create a tiny dummy file if it doesn't exist for logic testing
        if not os.path.exists(self.test_input):
            with open(self.test_input, "wb") as f:
                f.write(b"\x00" * 1024)

    def test_extension_logic(self):
        formats = ["mp4", "mkv", "mp3", "wav"]
        for fmt in formats:
            out_path = f"test_output.{fmt}"
            engine = OptimizationEngine(self.test_input, out_path, "libx264", 24)
            self.assertTrue(engine.output_path.endswith(fmt))

    def tearDown(self):
        if os.path.exists(self.test_input):
            os.remove(self.test_input)

if __name__ == "__main__":
    unittest.main()
