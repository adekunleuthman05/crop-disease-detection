import io
import unittest

from app import create_app


class UploadValidationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test", "UPLOAD_FOLDER": "instance/test-uploads"}).test_client()

    def test_page_loads(self):
        self.assertEqual(self.app.get("/").status_code, 200)

    def test_rejects_non_image_extension(self):
        response = self.app.post("/predict", data={"image": (io.BytesIO(b"not image"), "note.txt")}, follow_redirects=True)
        self.assertIn(b"Use a PNG", response.data)


if __name__ == "__main__":
    unittest.main()
