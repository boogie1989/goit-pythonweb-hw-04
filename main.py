import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
from argparse import ArgumentParser
import logging
from typing import Union

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

async def read_folder(source_path: Union[str, AsyncPath], output_path: Union[str, AsyncPath]) -> None:
    source = AsyncPath(source_path)
    target = AsyncPath(output_path)

    if not await source.exists():
        logging.error(f'Source path "{source}" not found.')
        return

    tasks = []

    async for element in source.iterdir():
        if await element.is_dir():
            tasks.append(read_folder(element, target))
        elif await element.is_file():
            tasks.append(copy_file(element, target))

    await asyncio.gather(*tasks, return_exceptions=True)

async def copy_file(file: AsyncPath, target_base: AsyncPath) -> None:
    try:
        suffix = file.suffix.lower().lstrip(".") or "unknown"
        target_dir = target_base / suffix
        await target_dir.mkdir(parents=True, exist_ok=True)

        target_path = target_dir / file.name
        await copyfile(file, target_path)
        logging.info(f"Copied: {file} -> {target_path}")

    except Exception as e:
        logging.error(f"Failed to copy {file}: {e}")

async def main() -> None:
    parser = ArgumentParser(description="Asynchronously copy and sort files by extension.")
    parser.add_argument("-s", "--source", type=str, required=True, help="Source directory")
    parser.add_argument("-t", "--target", type=str, required=True, help="Target directory")
    args = parser.parse_args()

    await read_folder(args.source, args.target)

if __name__ == "__main__":
    asyncio.run(main())
