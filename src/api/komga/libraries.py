from typing import List

from src.config import KOMGA_BASE_URL
from src.model.komga.common import KomgaHeaders
from src.model.komga.library import KomgaLibrary
from src.service import new_async_client
from ._helper import handle_resp


class KomgaLibrariesAPI:
    @staticmethod
    async def list() -> List[KomgaLibrary]:
        async with new_async_client(KomgaHeaders.GET, KOMGA_BASE_URL) as client:
            resp = handle_resp(await client.get("/api/v1/libraries"))
            return [KomgaLibrary().from_json(lib) for lib in resp]

    @staticmethod
    async def create(name: str, root: str) -> KomgaLibrary:
        async with new_async_client(KomgaHeaders.POST, KOMGA_BASE_URL) as client:
            library = KomgaLibrary.new(name, root)
            if library.scan_directory_exclusions is None:
                library.scan_directory_exclusions = ['#recycle', '@Recycle', '@eaDir']
            resp = handle_resp(await client.post("/api/v1/libraries", json = library.get_payload()))
            return KomgaLibrary().from_json(resp)

    @staticmethod
    async def delete(library_id: str) -> None:
        async with new_async_client(KomgaHeaders.DEL, KOMGA_BASE_URL) as client:
            return handle_resp(await client.delete(f"/api/v1/libraries/{library_id}"))

    @staticmethod
    async def get(library_id: str) -> KomgaLibrary:
        async with new_async_client(KomgaHeaders.GET, KOMGA_BASE_URL) as client:
            resp = handle_resp(await client.get(f"/api/v1/libraries/{library_id}"))
            return KomgaLibrary().from_json(resp)

    @staticmethod
    async def update(library_id: str, library: KomgaLibrary) -> KomgaLibrary:
        async with new_async_client(KomgaHeaders.PUT, KOMGA_BASE_URL) as client:
            return handle_resp(await client.patch(f"/api/v1/libraries/{library_id}", json = library.get_payload()))

    @staticmethod  # unstable
    async def analyze(library_id: str) -> None:
        async with new_async_client(KomgaHeaders.ANALYZE, KOMGA_BASE_URL) as client:
            return handle_resp(await client.post(f"/api/v1/libraries/{library_id}/analyze"))

    @staticmethod
    async def empty_trash(library_id: str) -> None:
        async with new_async_client(KomgaHeaders.DEL, KOMGA_BASE_URL) as client:
            return handle_resp(await client.post(f"/api/v1/libraries/{library_id}/empty-trash"))

    @staticmethod  # unstable
    async def refresh_metadata(library_id: str) -> None:
        async with new_async_client(KomgaHeaders.ANALYZE, KOMGA_BASE_URL) as client:
            return handle_resp(await client.post(f"/api/v1/libraries/{library_id}/metadata/refresh"))

    @staticmethod
    async def scan(library_id: str, deep: bool = False) -> None:
        async with new_async_client(KomgaHeaders.ANALYZE, KOMGA_BASE_URL) as client:
            return handle_resp(await client.post(f"/api/v1/libraries/{library_id}/scan", json = {"deep": deep}))
