from ..config import plugin_config

if plugin_config.sd_api:
    from .stable_diffusion import gennerate  # noqa: F401
elif plugin_config.nai3_token:
    from .novelai import gennerate  # noqa: F401