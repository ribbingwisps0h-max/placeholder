"""
Tests for Placeholder Image Service.
"""
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.generator import PlaceholderConfig, create_placeholder

client = TestClient(app)


# ── Generator unit tests ─────────────────────────────────────

class TestGenerator:
    def test_default_config(self):
        cfg = PlaceholderConfig()
        buf = create_placeholder(cfg)
        assert isinstance(buf, io.BytesIO)
        img = Image.open(buf)
        assert img.size == (800, 600)

    def test_custom_size(self):
        cfg = PlaceholderConfig(width=200, height=100)
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.size == (200, 100)

    def test_jpeg_format(self):
        cfg = PlaceholderConfig(fmt="JPEG")
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.format == "JPEG"

    def test_webp_format(self):
        cfg = PlaceholderConfig(fmt="WEBP")
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.format == "WEBP"

    def test_gradient(self):
        cfg = PlaceholderConfig(
            gradient=True,
            gradient_colors=["#ff0000", "#0000ff"],
            gradient_angle=90,
        )
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.size == (800, 600)

    def test_three_color_gradient(self):
        cfg = PlaceholderConfig(
            gradient=True,
            gradient_colors=["#ff0000", "#00ff00", "#0000ff"],
        )
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.mode in ("RGB", "RGBA")

    def test_custom_text(self):
        cfg = PlaceholderConfig(text="Hello World", font_size=40)
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.size == (800, 600)

    def test_clamp_dimensions(self):
        cfg = PlaceholderConfig(width=9999, height=9999)
        buf = create_placeholder(cfg)
        img = Image.open(buf)
        assert img.width <= 5000
        assert img.height <= 5000


# ── API endpoint tests ───────────────────────────────────────

class TestAPI:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_gen_defaults(self):
        r = client.get("/api/gen")
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"

    def test_gen_size(self):
        r = client.get("/api/gen?w=300&h=200")
        assert r.status_code == 200
        img = Image.open(io.BytesIO(r.content))
        assert img.size == (300, 200)

    def test_gen_jpeg(self):
        r = client.get("/api/gen?fmt=JPEG")
        assert r.status_code == 200
        assert "jpeg" in r.headers["content-type"]

    def test_gen_webp(self):
        r = client.get("/api/gen?fmt=WEBP")
        assert r.status_code == 200
        assert "webp" in r.headers["content-type"]

    def test_gen_text(self):
        r = client.get("/api/gen?text=Hello")
        assert r.status_code == 200
        img = Image.open(io.BytesIO(r.content))
        assert img.size == (400, 300)

    def test_gen_gradient(self):
        r = client.get("/api/gen?gradient=true&gc=ff0000,0000ff&ga=45")
        assert r.status_code == 200

    def test_gen_download_header(self):
        r = client.get("/api/gen?download=true")
        assert "attachment" in r.headers.get("content-disposition", "")

    def test_gen_invalid_hex(self):
        # invalid background color
        r = client.get("/api/gen?bg=ZZZZZZ")
        assert r.status_code == 422

    def test_gen_invalid_text_color(self):
        # text color should be validated independently
        r = client.get("/api/gen?tc=GGGGGG")
        assert r.status_code == 422

    def test_gen_img_tag_url(self):
        """Simulate embedding as <img src='...'> — should return binary."""
        r = client.get("/api/gen?w=300&h=200&text=Hello&bg=4a90d9")
        assert r.status_code == 200
        img = Image.open(io.BytesIO(r.content))
        assert img.size == (300, 200)

    def test_ui_page(self):
        r = client.get("/")
        assert r.status_code == 200
        assert "PH" in r.text
