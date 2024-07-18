import logging
import os
from typing import Union
from datetime import datetime, timezone
from azure.data.tables.aio import TableClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError


class Record:
    def __init__(
        self,
        user_id: str,
        note: str,
        version: int,
        decision: bool,
        updated_at: datetime,
    ):
        self.user_id = user_id
        self.note = note
        self.version = version
        self.decision = decision
        self.updated_at = updated_at


class AzureTableStorageHelper:
    """
    Implements interation with Azure Table Storage
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        storage_account_name = os.environ["STORAGE_ACCOUNT_NAME"]
        endpoint = f"https://{storage_account_name}.table.core.windows.net"
        table_name = os.environ["STORAGE_TABLE_NAME"]
        credential = DefaultAzureCredential()
        self._table_client = TableClient(endpoint, table_name, credential=credential)

    async def set_record(self, data: Record) -> None:
        self._logger.info("set_records: data: %s", data)
        entity = {
            "PartitionKey": data.user_id,
            "RowKey": f"{data.user_id}",
            "Note": data.note,
            "Version": data.version,
            "Decision": data.decision,
            "UpdatedAt": data.updated_at,
        }
        await self.__get_client().upsert_entity(entity=entity)

    async def get_record(self, user_id: str) -> Union[Record, None]:
        self._logger.info("get_record: user_id: %s", user_id)
        try:
            entity = await self.__get_client().get_entity(user_id, f"{user_id}")
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

    def __get_client(self):
        return self._table_client
