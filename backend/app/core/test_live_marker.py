"""The opt-in `live` marker really reaches the real Atlas *_test database (skipped by default;
run with `pytest -m live`)."""

from typing import Any

import pytest


@pytest.mark.live
async def test_live_db_is_real_atlas_test_db(db: Any) -> None:
    assert type(db).__module__.startswith("motor"), type(db)
    assert db.name.endswith("_test")
    res = await db.zz_tr_live_probe.insert_one({"zz_tr_probe": True})
    try:
        assert (await db.zz_tr_live_probe.find_one({"_id": res.inserted_id}))["zz_tr_probe"] is True
    finally:
        await db.zz_tr_live_probe.delete_one({"_id": res.inserted_id})  # exact id cleanup


async def test_default_db_is_the_in_process_fake(db: Any) -> None:
    assert type(db).__module__ == "fake_mongo", type(db)
