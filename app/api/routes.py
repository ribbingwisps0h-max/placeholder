"""
REST API endpoints for the Placeholder Service.
"""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.core.generator import PlaceholderConfig, create_placeholder

router = APIRouter(prefix="/api", tags=["generate"])

MIME = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
}


@router.get(
    "/gen",
    summary="Generate placeholder image",
    response_description="Binary image data",
    responses={
        200: {"content": {"image/png": {}, "image/jpeg": {}, "image/webp": {}}},
    },
)
async def generate(
    w: Annotated[int, Query(ge=1, le=5000, description="Width in pixels")] = 400,
    h: Annotated[int, Query(ge=1, le=5000, description="Height in pixels")] = 300,
    bg: Annotated[str, Query(description="Background HEX color (e.g. cccccc)")] = "cccccc",
    gradient: Annotated[bool, Query(description="Enable gradient background")] = False,
    gc: Annotated[
        str,
        Query(description="Gradient colors, comma-separated HEX (e.g. 4facfe,00f2fe,a18cd1)"),
    ] = "4facfe,00f2fe",
    ga: Annotated[int, Query(ge=0, le=360, description="Gradient angle in degrees")] = 135,
    text: Annotated[str, Query(max_length=200, description="Overlay text")] = "",
    tc: Annotated[str, Query(description="Text HEX color")] = "333333",
    fs: Annotated[int, Query(ge=0, le=500, description="Font size (0 = auto)")] = 0,
    fmt: Annotated[
        Literal["PNG", "JPEG", "WEBP"],
        Query(description="Output format"),
    ] = "PNG",
    q: Annotated[int, Query(ge=1, le=100, description="JPEG/WEBP quality")] = 90,
    download: Annotated[bool, Query(description="Force file download")] = False,
):
    def _fix_hex(raw: str) -> str:
        raw = raw.lstrip("#").strip()
        # must be either 3 or 6 hex characters
        if len(raw) not in (3, 6):
            raise HTTPException(422, detail=f"Invalid HEX color: '{raw}'")
        # ensure all characters are valid hex digits
        if not all(c in "0123456789abcdefABCDEF" for c in raw):
            raise HTTPException(422, detail=f"Invalid HEX color: '{raw}'")
        return "#" + raw

    try:
        bg_hex = _fix_hex(bg)
        text_hex = _fix_hex(tc)
        grad_colors = [_fix_hex(c) for c in gc.split(",") if c.strip()]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(422, detail=str(exc)) from exc

    cfg = PlaceholderConfig(
        width=w,
        height=h,
        bg_color=bg_hex,
        gradient=gradient,
        gradient_colors=grad_colors if len(grad_colors) >= 2 else ["#4facfe", "#00f2fe"],
        gradient_angle=ga,
        text=text,
        text_color=text_hex,
        font_size=fs,
        fmt=fmt,
        quality=q,
    )

    buf = create_placeholder(cfg)
    media_type = MIME[fmt]
    filename = f"placeholder_{w}x{h}.{fmt.lower()}"

    headers: dict[str, str] = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    else:
        headers["Content-Disposition"] = f'inline; filename="{filename}"'

    return StreamingResponse(buf, media_type=media_type, headers=headers)
