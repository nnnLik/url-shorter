from loguru import logger

from core.taskiq_broker import broker


async def exec_task_by_name(task_name: str, **kwargs: dict) -> None:
    task = broker.find_task(task_name)
    if not task:
        logger.error(f'Task not found: {task_name}')
        raise ValueError(f'Task not found: {task_name}')

    await task.kiq(**kwargs)
    logger.debug(f'Task {task_name} sent to queue')
