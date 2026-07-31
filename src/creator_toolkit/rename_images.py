from pathlib import Path


def rename_images(folder: str):
    path = Path(folder)

    if not path.exists():
        print("Folder not found.")
        return

    images = list(path.glob("*.jpg")) + list(path.glob("*.png"))

    print(f"Found {len(images)} image(s).")

    for index, image in enumerate(images, start=1):
        new_name = f"image_{index}{image.suffix}"
        image.rename(path / new_name)
        print(f"{image.name} -> {new_name}")