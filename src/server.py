import asyncio
from pathlib import Path

import aiofiles
from aiohttp import web

CHUNK_SIZE = 1024 * 256


async def archive(request: web.Request) -> web.StreamResponse:
    archive_hash = request.match_info["archive_hash"]
    folder_path = (Path("../test_photos") / archive_hash).resolve()

    proc = await asyncio.create_subprocess_exec(
        "zip",
        "-r",
        "-",
        ".",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=folder_path,
    )

    response = web.StreamResponse()
    archive_filename = "photos.zip"
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{archive_filename}"'
    )
    await response.prepare(request)

    try:
        while True:
            chunk = await proc.stdout.read(CHUNK_SIZE)
            if not chunk:
                break
            await response.write(chunk)
    finally:
        await proc.wait()

    return response


async def handle_index_page(request: web.Request) -> web.Response:
    async with aiofiles.open("index.html", mode="r") as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type="text/html")


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(
        [
            web.get("/", handle_index_page),
            web.get("/archive/{archive_hash}/", archive),
        ]
    )
    web.run_app(app)
