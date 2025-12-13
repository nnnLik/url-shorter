import logging
import os
from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Env(StrEnum):
    DEV = 'dev'
    PROD = 'prod'


class AppSettings(BaseSettings):
    TITLE: str = 'URL Shorter'
    DESCRIPTION: str = 'URL Shorter is a service that shortens URLs'
    VERSION: str = '0.1.0'

    ENV: Env = Field(Env.DEV, env='ENV')

    HOST: str = Field('0.0.0.0', env='HOST')
    PORT: int = Field(6749, env='PORT')
    RELOAD: bool = Field(False, env='RELOAD')
    BASE_URL: str = Field('http://localhost:9898', env='BASE_URL')

    @property
    def WORKERS(self) -> int:
        if self.ENV == Env.PROD:
            return os.cpu_count() or 1
        return 1


class TaskiqConfig(BaseSettings):
    BROKER_URL: str = Field('amqp://guest:guest@rabbitmq:5672/', env='TASKIQ_BROKER_URL')
    LOG_FORMAT: str = Field('%(asctime)s - %(name)s - %(levelname)s - %(message)s', env='TASKIQ_LOG_FORMAT')
    DATE_FORMAT: str = Field('%Y-%m-%d %H:%M:%S', env='TASKIQ_DATE_FORMAT')
    LOG_LEVEL: int = Field(logging.INFO, env='TASKIQ_LOG_LEVEL')


class DatabaseConfig(BaseSettings):
    URL: PostgresDsn = Field(
        'postgresql://url-shorter:url-shorter@url-shorter-postgres:5432/url-shorter', env='DATABASE_URL'
    )
    ECHO: bool = Field(False, env='ECHO')
    ECHO_POOL: bool = Field(False, env='ECHO_POOL')
    POOL_SIZE: int = Field(50, env='POOL_SIZE')
    MAX_OVERFLOW: int = Field(10, env='MAX_OVERFLOW')


class RedisConfig(BaseSettings):
    URL: str = Field('redis://url-shorter-redis:6379', env='REDIS_URL')
    DECODE_RESPONSES: bool = Field(True, env='REDIS_DECODE_RESPONSES')
    SOCKET_CONNECT_TIMEOUT: int = Field(5, env='REDIS_SOCKET_CONNECT_TIMEOUT')
    SOCKET_TIMEOUT: int = Field(5, env='REDIS_SOCKET_TIMEOUT')
    MAX_CONNECTIONS: int = Field(50, env='REDIS_MAX_CONNECTIONS')


@dataclass
class Settings:
    app: AppSettings
    database: DatabaseConfig
    taskiq: TaskiqConfig
    redis: RedisConfig

    @classmethod
    def build(cls) -> Self:
        return cls(
            app=AppSettings(),
            database=DatabaseConfig(),
            taskiq=TaskiqConfig(),
            redis=RedisConfig(),
        )
