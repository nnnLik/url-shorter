REFILL_CODE_POOL__TASK_NAME: str = "tasks.refill_code_pool_task:refill_code_pool_task"
PROCESS_CLICK__TASK_NAME: str = "tasks.process_click_task:process_click_task"
PROCESS_BATCH_CLICKS__TASK_NAME: str = "tasks.process_batch_clicks_task:process_batch_clicks_task"

PROCESS_CLICK_TASK__QUEUE_NAME: str = "click_processing"
CLICK_EVENTS_QUEUE_NAME: str = "click_events"

BATCH_CLICK_PROCESSING_BATCH_SIZE: int = 100
BATCH_CLICK_PROCESSING_TIMEOUT_SEC: float = 1.0
BATCH_CLICK_PROCESSING_INTERVAL_MIN: int = 1  # Интервал в минутах для cron

BASE62_CHARS: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
CODE_LENGTH: int = 8

CODE_POOL_MIN_SIZE: int = 10_000
CODE_POOL_MAX_SIZE: int = 50_000
CODE_POOL_REFILL_THRESHOLD: int = 5_000
CODE_POOL_BATCH_SIZE: int = 1_000
CODE_POOL_REFILL_INTERVAL_SEC: int = 300

CACHE_LINK_TTL_SEC: int = 86400  # 24 часа

DURABLE_CLICK_EVENTS_QUEUE_NAME: str = "click_events"
