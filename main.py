import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
from argparse import ArgumentParser
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


# Recursively reads the source folder and copies files to the target folder
async def read_folder(source_path: str | AsyncPath, output_path: str):
    if source_path is None or output_path is None:
        logging.error(f"Source path & Target path are required.")
        return

    source = AsyncPath(source_path)
    if not await source.exists():
        logging.error(f'Source path "{source_path}" not found.')
        return

    # Iterate over each element in the source folder
    async for element in source.iterdir():
        if await element.is_dir():
            # If the element is a directory, recursively call read_folder
            await read_folder(element, output_path)
        else:
            # If the element is a file, copy it to the target folder
            await copy_file(element, output_path)


# Copies a file to the target folder, organized by suffix
async def copy_file(file: AsyncPath, output_path: str):
    suffix = file.suffix.lower()[1:] or "unknown"
    target_path = AsyncPath(output_path) / suffix

    # Create the target folder if it doesn't exist
    await target_path.mkdir(parents=True, exist_ok=True)
    target_file_path = target_path / file.name
    try:
        # Copy the file to the target folder
        await copyfile(file, target_file_path)
        logging.info(f"{file} -> {target_file_path}")
    except Exception as err:
        logging.error(f"{file} -> {target_file_path}")
        logging.error(err)


# Main function to parse arguments and start the file copying process
async def main():
    parser = ArgumentParser(description="Copy & sort files by their suffixes.")
    parser.add_argument("-s", "--source", type=str, help="Source Path", required=True)
    parser.add_argument("-t", "--target", type=str, help="Target Path", required=True)

    args = parser.parse_args()
    await read_folder(args.source, args.target)


if __name__ == "__main__":
    asyncio.run(main())
