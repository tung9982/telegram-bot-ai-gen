"""Core utilities for generating AI-driven T-shirt mockups."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover - torch is optional
    torch = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from diffusers import DiffusionPipeline
    from diffusers.schedulers import DPMSolverMultistepScheduler
except Exception:  # pragma: no cover - diffusers is optional
    DiffusionPipeline = None  # type: ignore
    DPMSolverMultistepScheduler = None  # type: ignore

try:
    from PIL import Image, ImageDraw
except Exception as exc:  # pragma: no cover - fail early with clear message
    raise ImportError(
        "Pillow is required to use MockupGenerator. Install it with 'pip install Pillow'."
    ) from exc

LOGGER = logging.getLogger(__name__)


def _hex_to_rgba(color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert a hex color string to an RGBA tuple."""

    color = color.strip().lstrip("#")
    if len(color) not in {3, 6}:
        raise ValueError(f"Color '{color}' must be 3 or 6 hex digits long")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)
    return red, green, blue, alpha


@dataclass
class MockupRequest:
    """Configuration for generating a mockup."""

    prompt: str
    negative_prompt: str = ""
    guidance_scale: float = 7.5
    inference_steps: int = 30
    shirt_color: str = "#FFFFFF"
    background_color: str = "#F5F5F5"
    design_output: Optional[Path] = None
    mockup_output: Optional[Path] = None
    seed: Optional[int] = None


@dataclass
class MockupResult:
    """Details about a generated mockup."""

    request: MockupRequest
    design_path: Path
    mockup_path: Path


class MockupGenerator:
    """Generate AI-powered T-shirt mockups using Stable Diffusion pipelines."""

    def __init__(
        self,
        model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
        output_dir: Path | str = "outputs",
        device: Optional[str] = None,
        use_dpm_scheduler: bool = True,
    ) -> None:
        self.model_id = model_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.use_dpm_scheduler = use_dpm_scheduler
        self._pipeline: Optional[DiffusionPipeline] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(self, request: MockupRequest) -> MockupResult:
        """Generate a mockup according to the provided request."""

        LOGGER.info("Generating design for prompt: %s", request.prompt)
        design_image = self._generate_design_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.inference_steps,
            seed=request.seed,
        )

        design_output = request.design_output or (self.output_dir / "design.png")
        design_path = self._persist_image(design_image, design_output)

        LOGGER.info("Compositing mockup for shirt color %s", request.shirt_color)
        mockup_image = self._compose_mockup(
            design_image,
            shirt_color=request.shirt_color,
            background_color=request.background_color,
        )

        mockup_output = request.mockup_output or (self.output_dir / "mockup.png")
        mockup_path = self._persist_image(mockup_image, mockup_output)

        return MockupResult(
            request=request,
            design_path=design_path,
            mockup_path=mockup_path,
        )

    def compose_from_design(
        self,
        design_image: Image.Image,
        shirt_color: str = "#FFFFFF",
        background_color: str = "#F5F5F5",
        output_path: Optional[Path] = None,
    ) -> Path:
        """Create a mockup using a pre-existing design image."""

        mockup = self._compose_mockup(
            design_image,
            shirt_color=shirt_color,
            background_color=background_color,
        )
        path = output_path or (self.output_dir / "mockup.png")
        return self._persist_image(mockup, path)

    # ------------------------------------------------------------------
    # Pipeline helpers
    # ------------------------------------------------------------------
    def _ensure_pipeline(self) -> DiffusionPipeline:
        if self._pipeline is not None:
            return self._pipeline
        if DiffusionPipeline is None:
            raise ImportError(
                "diffusers is required to generate designs. Install it with 'pip install diffusers torch'."
            )

        torch_dtype = None
        if torch is not None:
            torch_dtype = torch.float16 if self.device and "cuda" in self.device else torch.float32
        LOGGER.info("Loading diffusion pipeline %s", self.model_id)
        pipeline = DiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch_dtype,
            safety_checker=None,
        )

        if self.use_dpm_scheduler and DPMSolverMultistepScheduler is not None:
            pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)

        if self.device and torch is not None:
            pipeline = pipeline.to(self.device)

        self._pipeline = pipeline
        return pipeline

    def _generate_design_image(
        self,
        prompt: str,
        negative_prompt: str,
        guidance_scale: float,
        num_inference_steps: int,
        seed: Optional[int],
    ) -> Image.Image:
        pipeline = self._ensure_pipeline()
        generator = None
        if seed is not None and torch is not None:
            generator = torch.Generator(device=self.device or "cpu").manual_seed(seed)

        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            width=768,
            height=768,
            generator=generator,
        )
        image = result.images[0]
        return image

    # ------------------------------------------------------------------
    # Compositing helpers
    # ------------------------------------------------------------------
    def _compose_mockup(
        self,
        design_image: Image.Image,
        shirt_color: str,
        background_color: str,
    ) -> Image.Image:
        shirt_rgba = _hex_to_rgba(shirt_color)
        background_rgba = _hex_to_rgba(background_color)

        base, mask = self._render_base_template()
        colored_shirt = Image.new("RGBA", base.size, shirt_rgba)
        colored_shirt.putalpha(mask)

        background = Image.new("RGBA", base.size, background_rgba)
        mockup = Image.alpha_composite(background, colored_shirt)

        design_resized = self._prepare_design(design_image, base.size)
        position = self._design_position(base.size, design_resized.size)
        mockup.paste(design_resized, position, design_resized)

        mockup = Image.alpha_composite(mockup, base)
        return mockup.convert("RGB")

    def _prepare_design(self, image: Image.Image, template_size: Tuple[int, int]) -> Image.Image:
        design = image.convert("RGBA")
        width, height = template_size
        target_width = int(width * 0.45)
        target_height = int(height * 0.5)
        design.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        return design

    def _design_position(self, template_size: Tuple[int, int], design_size: Tuple[int, int]) -> Tuple[int, int]:
        width, height = template_size
        design_width, design_height = design_size
        x = width // 2 - design_width // 2
        y = int(height * 0.32)
        return x, y

    def _render_base_template(self) -> Tuple[Image.Image, Image.Image]:
        size = (1024, 1024)
        outline = Image.new("RGBA", size, (0, 0, 0, 0))
        mask = Image.new("L", size, 0)

        outline_draw = ImageDraw.Draw(outline)
        mask_draw = ImageDraw.Draw(mask)

        body = [(360, 200), (664, 200), (720, 420), (700, 840), (324, 840), (304, 420)]
        left_sleeve = [(304, 420), (220, 430), (232, 260), (340, 200)]
        right_sleeve = [(720, 420), (804, 430), (792, 260), (684, 200)]

        mask_draw.polygon(body, fill=255)
        mask_draw.polygon(left_sleeve, fill=255)
        mask_draw.polygon(right_sleeve, fill=255)

        def draw_outline(points: list[Tuple[int, int]]):
            outline_draw.line(points + [points[0]], fill=(70, 70, 70, 220), width=6, joint="curve")

        draw_outline(body)
        draw_outline(left_sleeve)
        draw_outline(right_sleeve)

        collar = [(420, 200), (604, 200), (580, 260), (444, 260)]
        outline_draw.line(collar + [collar[0]], fill=(90, 90, 90, 200), width=6, joint="curve")

        return outline, mask

    def _persist_image(self, image: Image.Image, path: Path) -> Path:
        path = Path(path)
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            path = path.with_suffix(".png")
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return path
