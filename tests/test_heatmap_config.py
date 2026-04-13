import unittest

from config_mejorado import Config


class HeatmapConfigTests(unittest.TestCase):
    def test_homogeneidad_configurada_por_modo(self):
        self.assertGreaterEqual(Config.HEATMAP_HOMOGENEIDAD_DIGITAL_MEDIAN, 1)
        self.assertGreaterEqual(Config.HEATMAP_HOMOGENEIDAD_DIGITAL_GAUSS, 1)
        self.assertGreaterEqual(Config.HEATMAP_HOMOGENEIDAD_TINTA_MEDIAN, 1)
        self.assertGreaterEqual(Config.HEATMAP_HOMOGENEIDAD_TINTA_GAUSS, 1)
        self.assertGreaterEqual(Config.HEATMAP_NIVELES_COLOR_DIGITAL, 2)
        self.assertGreaterEqual(Config.HEATMAP_NIVELES_COLOR_TINTA, 2)


if __name__ == "__main__":
    unittest.main()
