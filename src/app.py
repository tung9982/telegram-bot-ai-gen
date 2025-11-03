"""Command line interface for generating AI-driven T-shirt mockups."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from PIL import Image

from mockup_ai import MockupGenerator, MockupRequest

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI T-shirt mockups with Stable Diffusion")
    parser.add_argument("prompt", help="Positive prompt describing the T-shirt artwork")
    parser.add_argument("-n", "--negative-prompt", default="", help="Negative prompt to avoid unwanted details")
    parser.add_argument("-o", "--output", type=Path, default=Path("outputs/mockup.png"), help="Where to store the final mockup")
    parser.add_argument("--design-output", type=Path, default=Path("outputs/design.png"), help="Where to store the generated design image")
    parser.add_argument("--shirt-color", default="#FFFFFF", help="Hex color code for the shirt fabric")
    parser.add_argument("--background-color", default="#F5F5F5", help="Hex color code for the mockup background")
    parser.add_argument("--guidance-scale", type=float, default=7.5, help="Classifier-free guidance scale")
    parser.add_argument("--steps", type=int, default=30, help="Number of inference steps for Stable Diffusion")
    parser.add_argument("--seed", type=int, default=None, help="Seed for deterministic generation")
    parser.add_argument("--model", default="stabilityai/stable-diffusion-xl-base-1.0", help="Diffusion model id")
    parser.add_argument("--device", default=None, help="Torch device (e.g. 'cuda', 'cuda:0', or 'cpu')")
    parser.add_argument("--disable-dpm", action="store_true", help="Disable the DPM++ scheduler")
    parser.add_argument(
        "--design",
        type=Path,
        default=None,
        help="Use an existing design image instead of generating one with the diffusion model",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generator = MockupGenerator(
        model_id=args.model,
        output_dir=args.output.parent,
        device=args.device,
        use_dpm_scheduler=not args.disable_dpm,
    )

    if args.design is not None:
        design_image = Image.open(args.design)
        mockup_path = generator.compose_from_design(
            design_image,
            shirt_color=args.shirt_color,
            background_color=args.background_color,
            output_path=args.output,
        )
        LOGGER.info("Mockup saved to %s", mockup_path)
        return

    request = MockupRequest(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        guidance_scale=args.guidance_scale,
        inference_steps=args.steps,
        shirt_color=args.shirt_color,
        background_color=args.background_color,
        design_output=args.design_output,
        mockup_output=args.output,
        seed=args.seed,
    )

    result = generator.generate(request)
    LOGGER.info("Design saved to %s", result.design_path)
    LOGGER.info("Mockup saved to %s", result.mockup_path)


if __name__ == "__main__":
    main()
