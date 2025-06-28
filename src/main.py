import asyncio

CHUNK_SIZE = 1024 * 256


async def archive(folder_path, out_file):
    proc = await asyncio.create_subprocess_exec(
        "zip",
        "-r",
        "-",
        folder_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert proc.stdout is not None
    with open(out_file, "wb") as f:
        while True:
            chunk = await proc.stdout.read(CHUNK_SIZE)
            if not chunk:
                break
            f.write(chunk)

    assert proc.stderr is not None
    await proc.wait()
    if proc.returncode != 0:
        err = await proc.stderr.read()
        raise Exception(f"zip error: {err.decode()}")


async def main():
    await archive("../test_photos/", "archive.zip")


if __name__ == "__main__":
    asyncio.run(main())
