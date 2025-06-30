import argparse
import asyncio
import os

import aiofiles
from aiohttp import web

from loger_config import start_logger

CHUNK_SIZE = 1024 * 256


async def archive(request: web.Request) -> web.StreamResponse:
    photos_path = request.app.args.path
    archive_hash = request.match_info["archive_hash"]
    archive_path = os.path.join(photos_path, archive_hash)

    if not os.path.exists(archive_path):
        return web.Response(status=404, text="Архив не существует или был удален")

    proc = await asyncio.create_subprocess_exec(
        "zip",
        "-r",
        "-",
        ".",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=archive_path,
    )

    response = web.StreamResponse()
    archive_filename = "photos.zip"
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{archive_filename}"'
    )
    await response.prepare(request)

    try:
        while chunk := await proc.stdout.read(CHUNK_SIZE):
            if request.app.args.delay:
                await asyncio.sleep(1)
            if request.app.args.logging:
                logger.info("Sending archive chunk ...")
            await response.write(chunk)
    except (ConnectionResetError, BrokenPipeError):
        if request.app.args.logging:
            logger.warning("Download was interrupted")
    except asyncio.CancelledError:
        if proc.returncode is None:
            proc.kill()
            await proc.communicate()
        raise
    except BaseException as ex:
        if request.app.args.logging:
            logger.error(f"Unexpected error: {type(ex).__name__}: {ex}")
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()

    return response


def read_arguments():
    parser = argparse.ArgumentParser(description="Download microservice")
    parser.add_argument("-l", "--logging", action="store_true", help="Enable logging")
    parser.add_argument(
        "-d", "--delay", action="store_true", help="Enable response delay"
    )
    parser.add_argument("-p", "--path", default="test_photos", help="Photos path")

    args = parser.parse_args()
    return args


async def handle_index_page(request: web.Request) -> web.Response:
    async with aiofiles.open("index.html", mode="r") as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type="text/html")


if __name__ == "__main__":
    args = read_arguments()
    app = web.Application()
    logger = start_logger()
    app.args = args
    app.add_routes(
        [
            web.get("/", handle_index_page),
            web.get("/archive/{archive_hash}/", archive),
        ]
    )
    web.run_app(app)
