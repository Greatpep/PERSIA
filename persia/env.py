import os

from persia.logger import get_default_logger

_logger = get_default_logger()


class _Env:
    def __init__(self):
        self.replica_size = None
        self.replica_index = None
        self.world_size = None
        self.rank = None
        self.local_rank = None
        self.is_init = False

    def init(self):
        if self.is_init:
            return

        if os.environ.get("RANK", None):
            self.rank = int(os.environ["RANK"])
            self.local_rank = int(os.environ["LOCAL_RANK"])
            self.world_size = int(os.environ["WORLD_SIZE"])
            assert self.rank >= 0, "rank should not be a negative."
            assert self.local_rank >= 0, "local_rank should not be a negative."
            assert self.world_size >= 1, "world_size should greater than one."
        else:
            if "REPLICA_INDEX" in os.environ:
                self.replica_index = int(os.environ["REPLICA_INDEX"])
                self.replica_size = int(os.environ["REPLICA_SIZE"])
                assert (
                    self.replica_index >= 0
                ), "replica_index should not be a negative."
                assert self.replica_size >= 1, "replica_size should greater than one."
            else:
                _logger.warning(
                    "replica_index not found, use default replica_index=0 and default replica_size=1"
                )
                self.replica_size = 1
                self.replica_index = 0
        self.is_init = True


env = _Env()


def _ensure_parse_env(get_func):
    def func():
        if not env.is_init:
            env.init()
        return get_func()

    return func


@_ensure_parse_env
def get_world_size() -> int:
    """Get the total number of processes."""
    return env.world_size


@_ensure_parse_env
def get_rank() -> int:
    """Get the rank of current process."""
    return env.rank


@_ensure_parse_env
def get_local_rank() -> int:
    """Get the local rank of current process.

    Local rank is the rank of the process on the local machine."""
    return env.local_rank


@_ensure_parse_env
def get_replica_size() -> int:
    """Get the replica size of the current service.

    Replica size is the number of services launched by docker service or k8s"""
    return env.replica_size


@_ensure_parse_env
def get_replica_index() -> int:
    """Get the replica index of current service.

    The replica index is a unique identifier assigned to each replica. They are assigned following the order of launching.
    """
    return env.replica_index
