# SPDX-License-Identifier: AGPL-3.0-or-later
"""The daily OpenObserve -> NetBox ZFS health sync, as a NetBox system job (run by the rq worker)."""
from core.choices import JobIntervalChoices
from core.exceptions import JobFailed
from netbox.jobs import JobRunner, system_job
from . import sync


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class ZFSHealthSyncJob(JobRunner):
    class Meta:
        name = "ZFS health sync from OpenObserve"

    def run(self, *args, **kwargs):
        config = sync.OpenObserveConfig.from_env()
        if config is None:
            self.logger.info(f"Not configured: set {sync.ENV_PREFIX}URL, _USERNAME and _PASSWORD.")
            return
        result = sync.apply(sync.parse(sync.fetch(config)))
        self.logger.info(
            f"pools written {len(result.pools_written)}, unchanged {len(result.pools_unchanged)}; "
            f"members written {result.members_written}"
        )
        for guid in result.pools_unmatched:
            self.logger.warning(f"No pool with GUID {guid}")
        for label, rows in (("No vdev member for", result.members_unmatched), ("Several vdev members for", result.members_ambiguous)):
            for guid, serial, number in rows:
                self.logger.warning(f"{label} pool {guid}, serial {serial}, partition {number}")
        if not (result.pools_written or result.pools_unchanged):
            raise JobFailed("OpenObserve returned no ZFS readings for any known pool.")
