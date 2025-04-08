from pymisp import PyMISP
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MISP_URL: str
    MISP_KEY: str
    MISP_VERIFYCERT: bool

    model_config = SettingsConfigDict(env_file=".env")

env = Settings()
misp = PyMISP(env.MISP_URL, env.MISP_KEY, env.MISP_VERIFYCERT, debug=False)

start_timestamp = 1741564800 # March 11, 2025 (00:00:00 UTC)
end_timestamp = 1741737600   # March 13, 2025 (00:00:00 UTC):

r = misp.search(
    published=False, 
    timestamp=[start_timestamp, end_timestamp],
    metadata=True)
print(r)


# r = misp.search(
#     published=False, 
#     value="linux",
#     metadata=True)
# print(r)


# r = misp.search(
#     eventid=[5079],
#     published=False,
#     metadata=True)
# print(r)