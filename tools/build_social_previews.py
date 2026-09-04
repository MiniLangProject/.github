"""Build exact-text GitHub social previews from the shared MiniLang artwork."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "profile" / "assets"
OUTPUT = ASSETS / "social-previews"
BACKGROUND = ASSETS / "social-preview-background.png"
WIDTH = 1280
HEIGHT = 640

PROJECTS = {
    "MiniLangProject": (
        "LANGUAGE ECOSYSTEM",
        "Native. Self-hosted. Practical.",
        "One language  •  Two compilers  •  Windows & Linux x64",
        ("SELF-HOSTED", "NATIVE X64", "REAL APPLICATIONS"),
    ),
    "MiniLangCompilerML": (
        "SELF-HOSTED COMPILER",
        "MiniLangCompilerML",
        "MiniLang compiler  •  Native PE32+ & ELF64",
        ("SELF-HOSTED", "WINDOWS", "LINUX"),
    ),
    "MiniLangCompilerPy": (
        "REFERENCE COMPILER",
        "MiniLangCompilerPy",
        "Python bootstrap  •  Compatible native output",
        ("BOOTSTRAP", "WINDOWS", "LINUX"),
    ),
    "MiniDoc": (
        "DEVELOPER TOOLING",
        "MiniDoc",
        "Documentation generation  •  Static analysis",
        ("SELF-HOSTED", "HTML", "MARKDOWN"),
    ),
    "MiniSQL": (
        "DATABASE SERVER",
        "MiniSQL",
        "Transactional SQL  •  Concurrency, TLS & replication",
        ("TRANSACTIONS", "WINDOWS", "LINUX"),
    ),
    "MiniDoom": (
        "NATIVE GAME PORT",
        "MiniDoom",
        "DOOM engine  •  Classic & OpenGL renderers",
        ("MINILANG", "WINDOWS", "LINUX"),
    ),
    "MiniQuake": (
        "NATIVE GAME PORT",
        "MiniQuake",
        "Quake engine  •  Protocol 15  •  OpenGL",
        ("MINILANG", "WINDOWS", "LINUX"),
    ),
    "MiniQuake2": (
        "NATIVE GAME PORT",
        "MiniQuake2",
        "Quake II 3.19  •  Protocol 34",
        ("MINILANG", "WINDOWS", "X86-64"),
    ),
    "MiniPixels": (
        "2D GAME ENGINE",
        "MiniPixels",
        "Pixel-oriented native game development",
        ("SPRITES", "TILEMAPS", "OPENGL"),
    ),
    "MiniIDE": (
        "DEVELOPER TOOLING",
        "MiniIDE",
        "A lightweight native IDE for MiniLang",
        ("EDITOR", "BUILD & RUN", "WINDOWS"),
    ),
    "MiniGui": (
        "NATIVE UI LIBRARY",
        "MiniGui",
        "Declarative desktop interfaces for MiniLang",
        ("DECLARATIVE UI", "WIN32", "CODEGEN"),
    ),
}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a Windows UI font with stable metrics for the generated artwork."""

    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def fit_font(draw: ImageDraw.ImageDraw, text: str, maximum: int) -> ImageFont.FreeTypeFont:
    """Choose the largest title size that stays inside the safe text column."""

    for size in range(72, 43, -2):
        candidate = font("segoeuib.ttf", size)
        if draw.textbbox((0, 0), text, font=candidate)[2] <= maximum:
            return candidate
    return font("segoeuib.ttf", 42)


def rounded_tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> int:
    """Draw one compact feature tag and return the next horizontal position."""

    tag_font = font("seguisb.ttf", 17)
    box = draw.textbbox((0, 0), text, font=tag_font)
    width = box[2] - box[0] + 34
    draw.rounded_rectangle(
        (x, y, x + width, y + 40),
        radius=20,
        fill=(7, 31, 70, 220),
        outline=(31, 175, 255, 180),
        width=2,
    )
    draw.text((x + 17, y + 9), text, font=tag_font, fill=(211, 241, 255, 255))
    return x + width + 12


def base_image() -> Image.Image:
    """Prepare the shared background and darken its text-safe left side."""

    image = Image.open(BACKGROUND).convert("RGB").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(1.06).convert("RGBA")
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = shade.load()
    for x in range(WIDTH):
        alpha = int(max(0, 155 * (1 - x / 900)))
        for y in range(HEIGHT):
            pixels[x, y] = (1, 10, 31, alpha)
    return Image.alpha_composite(image, shade)


def build(name: str, data: tuple[str, str, str, tuple[str, ...]]) -> Path:
    """Render one repository preview with exact project text and shared styling."""

    eyebrow, title, subtitle, tags = data
    image = base_image()
    draw = ImageDraw.Draw(image, "RGBA")

    draw.rounded_rectangle((70, 58, 276, 94), radius=18, fill=(255, 151, 20, 235))
    draw.text((88, 66), "MINILANG PROJECT", font=font("segoeuib.ttf", 15), fill=(5, 21, 51, 255))
    draw.text((70, 132), eyebrow, font=font("seguisb.ttf", 20), fill=(48, 195, 255, 255))

    title_font = fit_font(draw, title, 760)
    draw.text((66, 180), title, font=title_font, fill=(246, 251, 255, 255), stroke_width=1, stroke_fill=(0, 17, 52, 220))
    draw.rectangle((70, 282, 170, 288), fill=(255, 157, 24, 255))
    draw.text((70, 319), subtitle, font=font("segoeui.ttf", 27), fill=(197, 226, 244, 255))

    x = 70
    for tag in tags:
        x = rounded_tag(draw, x, 452, tag)

    draw.text((70, 554), "github.com/MiniLangProject", font=font("segoeui.ttf", 20), fill=(129, 180, 216, 255))

    output_name = "minilang-project-hero.jpg" if name == "MiniLangProject" else f"{name}.jpg"
    target = ASSETS / output_name if name == "MiniLangProject" else OUTPUT / output_name
    target.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(target, "JPEG", quality=90, optimize=True, progressive=True)
    return target


def main() -> None:
    """Regenerate every organization and repository social-preview asset."""

    for name, data in PROJECTS.items():
        target = build(name, data)
        print(f"{target.relative_to(ROOT)} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
