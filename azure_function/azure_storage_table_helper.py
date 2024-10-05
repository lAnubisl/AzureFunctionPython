import os
import logging
from typing import Mapping, Any, Optional
from datetime import datetime, timezone
from azure.data.tables.aio import TableClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from record import Record


class AzureTableStorageHelper:
    """
    Implements interation with Azure Table Storage
    """

    def __init__(self):
        storage_account_name = os.environ["STORAGE_ACCOUNT_NAME"]
        self._endpoint = f"https://{storage_account_name}.table.core.windows.net"
        self._table_name = os.environ["STORAGE_TABLE_NAME"]

    async def set_record(self, data: Record) -> None:
        logging.info("Call: set_records(data: Record)")
        entity: Mapping[str, Any] = {
            "PartitionKey": data.user_id,
            "RowKey": data.user_id,
            "Note": data.note,
            "Version": data.version,
            "Decision": data.decision,
            "UpdatedAt": data.updated_at,
        }
        async with DefaultAzureCredential() as creds:
            async with TableClient(self._endpoint, self._table_name, credential=creds) as client:
                await client.upsert_entity(entity=entity)

    async def get_record(self, user_id: str) -> Optional[Record]:
        logging.info(f"get_record: user_id: {user_id}")
        async with DefaultAzureCredential() as creds:
            async with TableClient(self._endpoint, self._table_name, credential=creds) as client:
                try:
                    entity = await client.get_entity(partition_key=user_id, row_key=user_id)
                except ResourceNotFoundError:
                    return None

                upd = entity["UpdatedAt"]
                return Record(
                    user_id,
                    entity["Note"],
                    int(entity["Version"]),
                    bool(entity["Decision"]),
                    datetime(
                        upd.year,
                        upd.month,
                        upd.day,
                        upd.hour,
                        upd.minute,
                        upd.second,
                        upd.microsecond,
                        tzinfo=timezone.utc,
                    ),
                )
