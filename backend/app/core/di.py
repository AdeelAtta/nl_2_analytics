from dependency_injector import containers, providers

from app.core.config import Settings, get_settings
from app.core.database import async_session_factory


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.health",
        ]
    )

    settings: providers.Singleton[Settings] = providers.Singleton(
        get_settings
    )

    db_session_factory = providers.Factory(
        async_session_factory
    )
