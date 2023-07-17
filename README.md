# Poodle - Python Moodle

Poodle is an SDK intended for providing typed api interfacing with any Moodle instance.

It is part of a Bachelor Thesis and therefore only meant for educational purposes.

It is still work in progress.

## Installation

Poodle can be installed by running:
```shell
pip install bchmnn.poodle
```

## Basic Usage

```python
async def main(moodle: Poodle):
  course = await moodle.get_user_course("<some_course_name>")
  groups = await moodle.core_group_get_course_groups(course.id)
  assignment = await moodle.get_assignment(course.id, index=-1)
  participants = await moodle.mod_assign_list_participants(assignment.id)

async def setup():
  url = "https://your.moodle.instance"
  poodle = Poodle(url)
  async with poodle as moodle:
    await moodle.auth()
    await main(moodle)

if __name__ == "__main__":
  asyncio.run(setup())
```

## Advanced Usage

### Credential Provider

The default credential provider is `CLICredentialProvider` that retrieves credentials through the command line.

If you want to define your own credential provider:

```python
class CustomCredentialProvider(GenericCredentialProviderInterface):
  def __init__(self, id_provider_url="*", priority=3):
    super().__init__(id_provider_url, priority)

  def retrieve(self) -> Tuple[str, str]:
    # get credentials
    return (username, password)

  @property
  def name(self) -> str:
    return "PassCredentialProvider"
```

### Authentication Provider

The default authentication provider is `BrowserSSOHandler` that opens the `public_config.launchurl` in a browser and retrieves the token by registering a custom url schema. The OS will handle the callback and propagate the token.

If you want to define your own authentication provider:

```python
class CustomAuthHandler(AbstractSSOHandler):
  _login_providers: List[GenericCredentialProviderInterface]

  def __init__(
    self,
    id_provider_urls: List[str],
    priority: int = 0,
    login_providers: List[GenericCredentialProviderInterface] = [],
  ):
    super().__init__(priority, id_provider_urls)
    self.init_logger(LOGGER_NAME, level=LOGGING_LEVEL)
    self._login_providers = login_providers

  async def authenticate(
    self,
    public_config: CoreSitePublicConfig,
    session: aiohttp.ClientSession,
  ) -> Tokens:
    # fetch tokens
    return tokens
```

### Use Custom Providers

If you have defined your custom credential and authentication provider you can apply them:

```python
async def setup():
  url = "https://your.moodle.instance"

  login_provider = CustomCredentialProvider()
  auth_handler = CustomAuthHandler([url], priority=1, login_providers=[login_provider])

  poodle = Poodle(url, auth_handlers=[auth_handler])
  async with poodle as moodle:
    await moodle.auth()
    # do some stuff
```

## Features

- [ ] authentication using os browser
- [x] caching
- [ ] types
  - [x] core_webservice_get_site_info
  - [x] core_enrol_get_users_courses
  - [x] core_course_get_contents
  - [x] core_group_get_course_groups
  - [x] mod_assign_get_assignments
  - [x] mod_assign_get_submissions
  - [x] mod_assign_list_participants
  - [ ] more to come
