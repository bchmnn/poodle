from enum import IntEnum
from typing import List, Optional

from .jsonable import Jsonable
from .ws import CoreWSExternalWarning


class CoreSiteQRCodeType(Jsonable, IntEnum):
    QR_CODE_DISABLED = 0  # QR code disabled value
    QR_CODE_URL = 1  # QR code type URL value
    QR_CODE_LOGIN = 2  # QR code type login value


class CoreSiteIdentityProvider(Jsonable):
    name: Optional[str] = None  # The identity provider name.
    iconurl: Optional[str] = None  # The icon URL for the provider.
    url: Optional[str] = None  # The URL of the provider.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreSitePublicConfig(Jsonable):
    wwwroot: Optional[str] = None  # Site URL.
    httpswwwroot: Optional[str] = None  # Site https URL (if httpslogin is enabled).
    sitename: Optional[str] = None  # Site name.
    guestlogin: Optional[int] = None  # Whether guest login is enabled.
    rememberusername: Optional[
        int
    ] = None  # Values: 0 for No, 1 for Yes, 2 for optional.
    authloginviaemail: Optional[int] = None  # Whether log in via email is enabled.
    registerauth: Optional[str] = None  # Authentication method for user registration.
    forgottenpasswordurl: Optional[str] = None  # Forgotten password URL.
    authinstructions: Optional[str] = None  # Authentication instructions.
    authnoneenabled: Optional[int] = None  # Whether auth none is enabled.
    enablewebservices: Optional[int] = None  # Whether Web Services are enabled.
    enablemobilewebservice: Optional[
        int
    ] = None  # Whether the Mobile service is enabled.
    maintenanceenabled: Optional[int] = None  # Whether site maintenance is enabled.
    maintenancemessage: Optional[str] = None  # Maintenance message.
    logourl: Optional[str] = None  # The site logo URL.
    compactlogourl: Optional[str] = None  # The site compact logo URL.
    typeoflogin: Optional[
        int
    ] = None  # The type of login. 1 for app, 2 for browser, 3 for embedded.
    launchurl: Optional[str] = None  # SSO login launch URL.
    mobilecssurl: Optional[str] = None  # Mobile custom CSS theme.
    tool_mobile_disabledfeatures: Optional[str] = None  # Disabled features in the app.
    identityproviders: List[CoreSiteIdentityProvider] = []  # Identity providers.
    country: Optional[str] = None  # Default site country.
    agedigitalconsentverification: Optional[
        bool
    ] = None  # Whether age digital consent verification is enabled.
    supportname: Optional[
        str
    ] = None  # Site support contact name (only if age verification is enabled).
    supportemail: Optional[
        str
    ] = None  # Site support contact email (only if age verification is enabled).
    autolang: Optional[
        int
    ] = None  # Whether to detect default language from browser setting.
    lang: Optional[str] = None  # Default language for the site.
    langmenu: Optional[int] = None  # Whether the language menu should be displayed.
    langlist: Optional[str] = None  # Languages on language menu.
    locale: Optional[str] = None  # Sitewide locale.
    tool_mobile_minimumversion: Optional[
        str
    ] = None  # Minimum required version to access.
    tool_mobile_iosappid: Optional[str] = None  # IOS app's unique identifier.
    tool_mobile_androidappid: Optional[str] = None  # Android app's unique identifier.
    tool_mobile_setuplink: Optional[str] = None  # App download page.
    tool_mobile_qrcodetype: CoreSiteQRCodeType = CoreSiteQRCodeType.QR_CODE_URL
    warnings: List[CoreWSExternalWarning] = []

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "identityproviders" in keys:
            identityproviders = entries["identityproviders"]
            if identityproviders is not None:
                self.identityproviders = [
                    CoreSiteIdentityProvider(**entry) for entry in identityproviders
                ]

        if "warnings" in keys:
            warnings = entries["warnings"]
            if warnings is not None:
                self.warnings = [CoreWSExternalWarning(**entry) for entry in warnings]

        if "tool_mobile_qrcodetype" in keys:
            tool_mobile_qrcodetype = entries["tool_mobile_qrcodetype"]
            if tool_mobile_qrcodetype is not None:
                self.tool_mobile_qrcodetype = CoreSiteQRCodeType(tool_mobile_qrcodetype)


class CoreSiteFunction(Jsonable):
    name: str  # Function name.
    version: str  # The version number of the component to which the function belongs.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreSiteAdvancedFeature(Jsonable):
    name: str  # Feature name.
    value: int  # Feature value. Usually 1 means enabled.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreSiteInfoUserHomepage(Jsonable, IntEnum):
    HOMEPAGE_SITE = 0  # Site home.
    HOMEPAGE_MY = 1  # Dashboard.
    HOMEPAGE_MYCOURSES = 3  # My courses.


class CoreSiteInfo(Jsonable):
    sitename: str  # Site name.
    username: str  # Username.
    firstname: str  # First name.
    lastname: str  # Last name.
    fullname: str  # User full name.
    lang: str  # Current language.
    userid: int  # User id.
    siteurl: str  # Site url.
    userpictureurl: str  # The user profile picture.
    functions: List[CoreSiteFunction] = []
    downloadfiles: Optional[
        int
    ] = None  # 1 if users are allowed to download files, 0 if not.
    uploadfiles: Optional[
        int
    ] = None  # 1 if users are allowed to upload files, 0 if not.
    release: Optional[str] = None  # Moodle release number.
    version: Optional[str] = None  # Moodle version number.
    mobilecssurl: Optional[str] = None  # Mobile custom CSS theme.
    advancedfeatures: List[
        CoreSiteAdvancedFeature
    ] = []  # Advanced features availability.
    usercanmanageownfiles: Optional[
        bool
    ] = None  # True if the user can manage his own files.
    userquota: Optional[
        int
    ] = None  # User quota (bytes). 0 means user can ignore the quota.
    usermaxuploadfilesize: Optional[
        int
    ] = None  # User max upload file size (bytes). -1 means the user can ignore the upload file size.
    userhomepage: Optional[
        CoreSiteInfoUserHomepage
    ] = None  # The default home page for the user.
    userprivateaccesskey: Optional[
        str
    ] = None  # Private user access key for fetching files.
    siteid: Optional[int] = None  # Site course ID.
    sitecalendartype: Optional[str] = None  # Calendar type set in the site.
    usercalendartype: Optional[str] = None  # Calendar typed used by the user.
    userissiteadmin: Optional[bool] = None  # Whether the user is a site admin or not.
    theme: Optional[str] = None  # Current theme for the user.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "functions" in keys:
            functions = entries["functions"]
            if functions is not None:
                self.functions = [CoreSiteFunction(**entry) for entry in functions]

        if "advancedfeatures" in keys:
            advancedfeatures = entries["advancedfeatures"]
            if advancedfeatures is not None:
                self.advancedfeatures = [
                    CoreSiteAdvancedFeature(**entry) for entry in advancedfeatures
                ]

        if "userhomepage" in keys:
            userhomepage = entries["userhomepage"]
            if userhomepage is not None:
                self.userhomepage = CoreSiteInfoUserHomepage(userhomepage)
