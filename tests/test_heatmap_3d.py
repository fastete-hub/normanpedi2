import unittest

import numpy as np
from PIL import Image

from analysis_mejorado import ImageAnalyzer


class Heatmap3DTests(unittest.TestCase):
    def test_cuantizacion_reduce_niveles(self):
        gray = np.tile(np.arange(0, 256, dtype=np.uint8), (4, 1))
        mask = np.ones_like(gray, dtype=np.uint8) * 255
        out = ImageAnalyzer._cuantizar_niveles(gray, mask, niveles=8)
        niveles = np.unique(out[mask > 0])
        self.assertLessEqual(len(niveles), 8)

    def test_generar_mapa_3d_desde_heatmap(self):
        arr = np.zeros((80, 120, 3), dtype=np.uint8)
        arr[:] = [255, 255, 255]
        arr[20:60, 20:100] = [255, 60, 0]
        img = Image.fromarray(arr, mode="RGB")

        out = ImageAnalyzer.generar_mapa_calor_3d_desde_heatmap(img)
        self.assertIsInstance(out, Image.Image)
        self.assertGreater(out.width, 0)
        self.assertGreater(out.height, 0)


if __name__ == "__main__":
    unittest.main()
