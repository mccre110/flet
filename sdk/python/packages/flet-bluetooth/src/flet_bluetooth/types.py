"""Shared types for Flet Bluetooth central and peripheral services."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union

import flet as ft

if TYPE_CHECKING:
    from flet_bluetooth.bluetooth import Bluetooth
    from flet_bluetooth.bluetooth_peripheral import BluetoothPeripheral

__all__ = [
    "BluetoothAndroidScanCallbackType",
    "BluetoothAndroidScanMatchMode",
    "BluetoothAndroidScanMode",
    "BluetoothAndroidScanNumOfMatches",
    "BluetoothAndroidScanOptions",
    "BluetoothAvailabilityChangeEvent",
    "BluetoothAvailabilityState",
    "BluetoothCharacteristic",
    "BluetoothCharacteristicValueEvent",
    "BluetoothConnectionChangeEvent",
    "BluetoothConnectionPriority",
    "BluetoothConnectionState",
    "BluetoothDescriptor",
    "BluetoothDevice",
    "BluetoothErrorCode",
    "BluetoothException",
    "BluetoothLogLevel",
    "BluetoothPairingStateChangeEvent",
    "BluetoothQueueType",
    "BluetoothScanFilter",
    "BluetoothScanResultEvent",
    "BluetoothService",
    "BluetoothSubscriptionType",
    "BluetoothWebOptions",
    "CharacteristicProperty",
    "ExclusionFilter",
    "GattCharacteristic",
    "GattDescriptor",
    "GattService",
    "ManufacturerData",
    "ManufacturerDataFilter",
    "PeripheralAdvertisingState",
    "PeripheralAdvertisingStateChangeEvent",
    "PeripheralAttributePermission",
    "PeripheralAvailabilityState",
    "PeripheralCapabilities",
    "PeripheralCharacteristicReadEvent",
    "PeripheralCharacteristicWriteEvent",
    "PeripheralConnectionChangeEvent",
    "PeripheralDescriptorReadEvent",
    "PeripheralDescriptorWriteEvent",
    "PeripheralManufacturerData",
    "PeripheralMtuChangeEvent",
    "PeripheralServiceAddedEvent",
    "PeripheralSubscriptionChangeEvent",
    "unwrap_bluetooth_result",
]


# ── Client / shared enums ────────────────────────────────────────────────────


class BluetoothAvailabilityState(Enum):
    """Bluetooth adapter availability."""

    UNKNOWN = "unknown"
    RESETTING = "resetting"
    UNSUPPORTED = "unsupported"
    UNAUTHORIZED = "unauthorized"
    POWERED_OFF = "poweredOff"
    POWERED_ON = "poweredOn"


class BluetoothConnectionState(Enum):
    """Connection state of a remote BLE device."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    DISCONNECTING = "disconnecting"


class BluetoothQueueType(Enum):
    """How BLE commands are queued before execution."""

    NONE = "none"
    """Execute commands in parallel (no queue)."""

    PER_DEVICE = "perDevice"
    """One queue per device."""

    GLOBAL = "global"
    """Single global queue for all devices (safest default)."""


class BluetoothLogLevel(Enum):
    """Log verbosity for the underlying BLE implementation."""

    NONE = "none"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    VERBOSE = "verbose"


class BluetoothSubscriptionType(Enum):
    """Characteristic subscription mode."""

    NOTIFICATIONS = "notifications"
    INDICATIONS = "indications"


class BluetoothConnectionPriority(Enum):
    """Android connection priority hint."""

    BALANCED = "balanced"
    HIGH_PERFORMANCE = "highPerformance"
    LOW_POWER = "lowPower"


class CharacteristicProperty(Enum):
    """GATT characteristic properties (matches ``universal_ble``)."""

    BROADCAST = "broadcast"
    READ = "read"
    WRITE_WITHOUT_RESPONSE = "writeWithoutResponse"
    WRITE = "write"
    NOTIFY = "notify"
    INDICATE = "indicate"
    AUTHENTICATED_SIGNED_WRITES = "authenticatedSignedWrites"
    EXTENDED_PROPERTIES = "extendedProperties"


class BluetoothAndroidScanMode(Enum):
    """Android BLE scan mode."""

    BALANCED = "balanced"
    LOW_LATENCY = "lowLatency"
    LOW_POWER = "lowPower"
    OPPORTUNISTIC = "opportunistic"


class BluetoothAndroidScanCallbackType(Enum):
    """Android scan callback type flags."""

    ALL_MATCHES = "allMatches"
    FIRST_MATCH = "firstMatch"
    MATCH_LOST = "matchLost"
    ALL_MATCHES_AUTO_BATCH = "allMatchesAutoBatch"


class BluetoothAndroidScanMatchMode(Enum):
    """Android scan match mode."""

    AGGRESSIVE = "aggressive"
    STICKY = "sticky"


class BluetoothAndroidScanNumOfMatches(Enum):
    """Android number-of-matches setting."""

    ONE = "one"
    FEW = "few"
    MAX = "max"


class BluetoothErrorCode(Enum):
    """Structured error codes from the BLE stack."""

    UNKNOWN_ERROR = "unknownError"
    FAILED = "failed"
    NOT_SUPPORTED = "notSupported"
    NOT_IMPLEMENTED = "notImplemented"
    CHANNEL_ERROR = "channelError"
    BLUETOOTH_NOT_AVAILABLE = "bluetoothNotAvailable"
    BLUETOOTH_NOT_ENABLED = "bluetoothNotEnabled"
    BLUETOOTH_NOT_ALLOWED = "bluetoothNotAllowed"
    BLUETOOTH_UNAUTHORIZED = "bluetoothUnauthorized"
    DEVICE_DISCONNECTED = "deviceDisconnected"
    CONNECTION_TIMEOUT = "connectionTimeout"
    CONNECTION_FAILED = "connectionFailed"
    CONNECTION_REJECTED = "connectionRejected"
    CONNECTION_LIMIT_EXCEEDED = "connectionLimitExceeded"
    CONNECTION_ALREADY_EXISTS = "connectionAlreadyExists"
    CONNECTION_TERMINATED = "connectionTerminated"
    CONNECTION_IN_PROGRESS = "connectionInProgress"
    ILLEGAL_ARGUMENT = "illegalArgument"
    DEVICE_NOT_FOUND = "deviceNotFound"
    SERVICE_NOT_FOUND = "serviceNotFound"
    CHARACTERISTIC_NOT_FOUND = "characteristicNotFound"
    INVALID_SERVICE_UUID = "invalidServiceUuid"
    INVALID_CHARACTERISTIC_UUID = "invalidCharacteristicUuid"
    INVALID_OFFSET = "invalidOffset"
    INVALID_ATTRIBUTE_LENGTH = "invalidAttributeLength"
    INVALID_PDU = "invalidPdu"
    INVALID_HANDLE = "invalidHandle"
    READ_FAILED = "readFailed"
    READ_NOT_PERMITTED = "readNotPermitted"
    WRITE_FAILED = "writeFailed"
    WRITE_NOT_PERMITTED = "writeNotPermitted"
    WRITE_REQUEST_BUSY = "writeRequestBusy"
    INVALID_ACTION = "invalidAction"
    OPERATION_NOT_SUPPORTED = "operationNotSupported"
    OPERATION_TIMEOUT = "operationTimeout"
    OPERATION_CANCELLED = "operationCancelled"
    OPERATION_IN_PROGRESS = "operationInProgress"
    CHARACTERISTIC_DOES_NOT_SUPPORT_READ = "characteristicDoesNotSupportRead"
    CHARACTERISTIC_DOES_NOT_SUPPORT_WRITE = "characteristicDoesNotSupportWrite"
    CHARACTERISTIC_DOES_NOT_SUPPORT_WRITE_WITHOUT_RESPONSE = (
        "characteristicDoesNotSupportWriteWithoutResponse"
    )
    CHARACTERISTIC_DOES_NOT_SUPPORT_NOTIFY = "characteristicDoesNotSupportNotify"
    CHARACTERISTIC_DOES_NOT_SUPPORT_INDICATE = "characteristicDoesNotSupportIndicate"
    NOT_PAIRED = "notPaired"
    NOT_PAIRABLE = "notPairable"
    ALREADY_PAIRED = "alreadyPaired"
    PAIRING_FAILED = "pairingFailed"
    PAIRING_CANCELLED = "pairingCancelled"
    PAIRING_TIMEOUT = "pairingTimeout"
    PAIRING_NOT_ALLOWED = "pairingNotAllowed"
    AUTHENTICATION_FAILURE = "authenticationFailure"
    INSUFFICIENT_AUTHENTICATION = "insufficientAuthentication"
    INSUFFICIENT_AUTHORIZATION = "insufficientAuthorization"
    INSUFFICIENT_ENCRYPTION = "insufficientEncryption"
    INSUFFICIENT_KEY_SIZE = "insufficientKeySize"
    PROTECTION_LEVEL_NOT_MET = "protectionLevelNotMet"
    ACCESS_DENIED = "accessDenied"
    UNPAIRING_FAILED = "unpairingFailed"
    ALREADY_UNPAIRED = "alreadyUnpaired"
    SCAN_FAILED = "scanFailed"
    STOPPING_SCAN_IN_PROGRESS = "stoppingScanInProgress"
    WEB_BLUETOOTH_GLOBALLY_DISABLED = "webBluetoothGloballyDisabled"


class BluetoothException(Exception):
    """
    Raised when a Bluetooth invoke method fails on the Dart side.

    Dart methods return an envelope ``{"ok": true, "value": ...}`` on success
    or ``{"ok": false, "code": ..., "message": ...}`` on failure. Python unwraps
    the failure case into this exception.
    """

    def __init__(
        self,
        message: str,
        code: Optional[Union[BluetoothErrorCode, str]] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details
        if isinstance(code, BluetoothErrorCode):
            self.code: Union[BluetoothErrorCode, str, None] = code
        elif isinstance(code, str):
            try:
                self.code = BluetoothErrorCode(code)
            except ValueError:
                self.code = code
        else:
            self.code = BluetoothErrorCode.UNKNOWN_ERROR

    def __str__(self) -> str:
        code = self.code
        code_str = code.value if isinstance(code, BluetoothErrorCode) else code
        if code_str:
            return f"{code_str}: {self.message}"
        return self.message


def unwrap_bluetooth_result(result: Any) -> Any:
    """
    Unwrap a Dart invoke envelope.

    Args:
        result: Either a plain value or an envelope dict with an ``ok`` flag.

    Returns:
        The ``value`` field when ``ok`` is true, or ``result`` unchanged when
        it is not an envelope.

    Raises:
        BluetoothException: When the envelope reports failure.
    """
    if isinstance(result, dict) and "ok" in result:
        if result.get("ok"):
            return result.get("value")
        raise BluetoothException(
            message=str(result.get("message") or "Bluetooth operation failed"),
            code=result.get("code"),
            details=result.get("details"),
        )
    return result


# ── Peripheral enums ─────────────────────────────────────────────────────────


class PeripheralAttributePermission(Enum):
    """GATT attribute permissions for peripheral characteristics/descriptors."""

    READABLE = "readable"
    WRITEABLE = "writeable"
    READ_ENCRYPTION_REQUIRED = "readEncryptionRequired"
    WRITE_ENCRYPTION_REQUIRED = "writeEncryptionRequired"


class PeripheralAvailabilityState(Enum):
    """
    Peripheral readiness / availability (maps to upstream
    ``PeripheralReadinessState``).
    """

    UNKNOWN = "unknown"
    READY = "ready"
    BLUETOOTH_OFF = "bluetoothOff"
    UNAUTHORIZED = "unauthorized"
    UNSUPPORTED = "unsupported"


class PeripheralAdvertisingState(Enum):
    """Peripheral advertising lifecycle state."""

    IDLE = "idle"
    STARTING = "starting"
    ADVERTISING = "advertising"
    STOPPING = "stopping"
    ERROR = "error"


# ── Value types (client) ─────────────────────────────────────────────────────


@ft.value
class ManufacturerData:
    """Manufacturer-specific advertisement data."""

    company_id: int
    """Bluetooth company identifier."""

    payload: bytes = b""
    """Manufacturer payload bytes."""


@ft.value
class ManufacturerDataFilter:
    """Filter for manufacturer data in a scan."""

    company_identifier: int
    """Company identifier to match (hex or decimal, e.g. ``0x004C``)."""

    payload_prefix: Optional[bytes] = None
    """Optional prefix that advertised data must start with."""

    payload_mask: Optional[bytes] = None
    """Optional bit mask applied to ``payload_prefix`` (same length)."""


@ft.value
class ExclusionFilter:
    """Devices matching this filter are excluded from scan results."""

    services: list[str] = field(default_factory=list)
    """Service UUIDs that identify devices to exclude."""

    manufacturer_data_filter: list[ManufacturerDataFilter] = field(default_factory=list)
    """Manufacturer data filters for exclusion."""

    name_prefix: Optional[str] = None
    """Device name prefix to exclude."""


@ft.value
class BluetoothScanFilter:
    """Optional filter applied while scanning for BLE devices."""

    with_services: list[str] = field(default_factory=list)
    """Include devices advertising any of these service UUIDs."""

    with_name_prefix: list[str] = field(default_factory=list)
    """Include devices whose name starts with any of these prefixes."""

    with_manufacturer_data: list[ManufacturerDataFilter] = field(default_factory=list)
    """Include devices matching any of these manufacturer data filters."""

    exclusion_filters: list[ExclusionFilter] = field(default_factory=list)
    """Exclude devices matching these filters."""


@ft.value
class BluetoothAndroidScanOptions:
    """Android-specific scan options."""

    request_location_permission: Optional[bool] = None
    """Whether to request location permission on Android 12+ (API 31+)."""

    scan_mode: Optional[BluetoothAndroidScanMode] = None
    """Scan power/latency trade-off."""

    report_delay_millis: Optional[int] = None
    """Delay before delivering batched scan results (``0`` = immediate)."""

    callback_type: Optional[list[BluetoothAndroidScanCallbackType]] = None
    """Scan callback type flags."""

    match_mode: Optional[BluetoothAndroidScanMatchMode] = None
    """Hardware match mode."""

    num_of_matches: Optional[BluetoothAndroidScanNumOfMatches] = None
    """Number of matches to report per filter."""

    legacy: Optional[bool] = None
    """Whether to use legacy advertising only."""


@ft.value
class BluetoothWebOptions:
    """Web Bluetooth scan / request options."""

    optional_services: list[str] = field(default_factory=list)
    """Service UUIDs that should remain accessible after connecting."""

    optional_manufacturer_data: list[int] = field(default_factory=list)
    """Company identifiers to include in web advertisement results."""


@ft.value
class BluetoothDescriptor:
    """A GATT descriptor discovered on a characteristic."""

    uuid: str
    """Descriptor UUID."""


@ft.value
class BluetoothCharacteristic:
    """A GATT characteristic discovered on a service."""

    uuid: str
    """Characteristic UUID."""

    properties: list[CharacteristicProperty] = field(default_factory=list)
    """Supported characteristic properties."""

    descriptors: list[BluetoothDescriptor] = field(default_factory=list)
    """Descriptors belonging to this characteristic."""


@ft.value
class BluetoothService:
    """A GATT service discovered on a connected device."""

    uuid: str
    """Service UUID."""

    characteristics: list[BluetoothCharacteristic] = field(default_factory=list)
    """Characteristics belonging to this service."""


@ft.value
class BluetoothDevice:
    """A BLE peripheral discovered via scan or system devices."""

    device_id: str
    """Platform-specific device identifier."""

    name: Optional[str] = None
    """Advertised device name, if available."""

    rssi: Optional[int] = None
    """Received signal strength in dBm."""

    is_system_device: Optional[bool] = None
    """Whether the device is already connected at the system level."""

    paired: Optional[bool] = None
    """Whether the device is paired (when known)."""

    service_uuids: list[str] = field(default_factory=list)
    """Service UUIDs advertised by the device."""

    manufacturer_data_list: list[ManufacturerData] = field(default_factory=list)
    """Manufacturer-specific advertisement payloads."""

    service_data: dict[str, bytes] = field(default_factory=dict)
    """Service data keyed by service UUID."""

    timestamp: Optional[int] = None
    """Advertisement timestamp in milliseconds since epoch, if available."""


# ── Value types (peripheral) ─────────────────────────────────────────────────


@ft.value
class PeripheralManufacturerData:
    """Manufacturer-specific data included in advertisements."""

    company_identifier: int
    """Bluetooth SIG company identifier."""

    data: bytes
    """Manufacturer-specific payload bytes."""


@ft.value
class PeripheralCapabilities:
    """Platform capabilities for BLE peripheral mode."""

    supports_peripheral_mode: bool = False
    """Whether the current platform supports peripheral/GATT server mode."""

    supports_manufacturer_data_in_advertisement: bool = False
    """Whether manufacturer data can be included in advertisements."""

    supports_manufacturer_data_in_scan_response: bool = False
    """Whether manufacturer data can be included in scan responses."""

    supports_service_data_in_advertisement: bool = False
    """Whether service data can be included in advertisements."""

    supports_service_data_in_scan_response: bool = False
    """Whether service data can be included in scan responses."""

    supports_targeted_characteristic_update: bool = False
    """Whether characteristic updates can target a single connected device."""

    supports_advertising_timeout: bool = False
    """Whether advertising can be started with a timeout."""


@ft.value
class GattDescriptor:
    """A GATT descriptor in a peripheral service tree."""

    uuid: str
    """Descriptor UUID (16-bit, 32-bit, or 128-bit string)."""

    value: Optional[bytes] = None
    """
    Optional initial value seeded into the Dart value cache.

    Used to answer synchronous descriptor read requests.
    """

    permissions: list[PeripheralAttributePermission] = field(default_factory=list)
    """Descriptor attribute permissions."""


@ft.value
class GattCharacteristic:
    """A GATT characteristic in a peripheral service tree."""

    uuid: str
    """Characteristic UUID (16-bit, 32-bit, or 128-bit string)."""

    properties: list[CharacteristicProperty] = field(default_factory=list)
    """Characteristic properties advertised to centrals."""

    permissions: list[PeripheralAttributePermission] = field(default_factory=list)
    """Attribute permissions enforced by the local GATT server."""

    value: Optional[bytes] = None
    """
    Optional initial value seeded into the Dart value cache.

    Used to answer synchronous characteristic read requests. Update later with
    :meth:`flet_bluetooth.BluetoothPeripheral.update_characteristic_value`.
    """

    descriptors: list[GattDescriptor] = field(default_factory=list)
    """Descriptors belonging to this characteristic."""


@ft.value
class GattService:
    """A GATT service in a peripheral service tree."""

    uuid: str
    """Service UUID (16-bit, 32-bit, or 128-bit string)."""

    primary: bool = True
    """Whether this is a primary service (default ``True``)."""

    characteristics: list[GattCharacteristic] = field(default_factory=list)
    """Characteristics belonging to this service."""


# ── Client events ────────────────────────────────────────────────────────────


@dataclass
class BluetoothScanResultEvent(ft.Event["Bluetooth"]):
    """Fired when a BLE device is discovered during a scan."""

    device: BluetoothDevice
    """The discovered device."""


@dataclass
class BluetoothAvailabilityChangeEvent(ft.Event["Bluetooth"]):
    """Fired when Bluetooth adapter availability changes."""

    state: BluetoothAvailabilityState
    """The new availability state."""


@dataclass
class BluetoothConnectionChangeEvent(ft.Event["Bluetooth"]):
    """Fired when a device connection state changes."""

    device_id: str
    """Device identifier."""

    is_connected: bool
    """Whether the device is currently connected."""

    state: BluetoothConnectionState = BluetoothConnectionState.DISCONNECTED
    """High-level connection state derived from ``is_connected``."""

    error: Optional[str] = None
    """Optional error message associated with the change."""


@dataclass
class BluetoothCharacteristicValueEvent(ft.Event["Bluetooth"]):
    """Fired when a subscribed characteristic emits a new value."""

    device_id: str
    """Device identifier."""

    service_uuid: str
    """Service UUID of the characteristic."""

    characteristic_uuid: str
    """Characteristic UUID."""

    value: bytes
    """Characteristic value bytes."""


@dataclass
class BluetoothPairingStateChangeEvent(ft.Event["Bluetooth"]):
    """Fired when a device pairing state changes."""

    device_id: str
    """Device identifier."""

    is_paired: bool
    """Whether the device is paired."""


# ── Peripheral events ────────────────────────────────────────────────────────


@dataclass
class PeripheralCharacteristicReadEvent(ft.Event["BluetoothPeripheral"]):
    """Fired after Dart answers a characteristic read from the value cache."""

    device_id: str
    """Central device that requested the read."""

    characteristic_uuid: str
    """UUID of the characteristic that was read."""

    offset: int = 0
    """Read offset requested by the central."""

    value: bytes = b""
    """Bytes returned from the cache (possibly sliced by ``offset``)."""


@dataclass
class PeripheralCharacteristicWriteEvent(ft.Event["BluetoothPeripheral"]):
    """Fired after a characteristic write was accepted and cached."""

    device_id: str
    """Central device that wrote the value."""

    characteristic_uuid: str
    """UUID of the characteristic that was written."""

    offset: int = 0
    """Write offset requested by the central."""

    value: bytes = b""
    """Bytes written by the central."""


@dataclass
class PeripheralDescriptorReadEvent(ft.Event["BluetoothPeripheral"]):
    """Fired after Dart answers a descriptor read from the value cache."""

    device_id: str
    """Central device that requested the read."""

    characteristic_uuid: str
    """UUID of the parent characteristic."""

    descriptor_uuid: str
    """UUID of the descriptor that was read."""

    offset: int = 0
    """Read offset requested by the central."""

    value: bytes = b""
    """Bytes returned from the cache (possibly sliced by ``offset``)."""


@dataclass
class PeripheralDescriptorWriteEvent(ft.Event["BluetoothPeripheral"]):
    """Fired after a descriptor write was accepted and cached."""

    device_id: str
    """Central device that wrote the value."""

    characteristic_uuid: str
    """UUID of the parent characteristic."""

    descriptor_uuid: str
    """UUID of the descriptor that was written."""

    offset: int = 0
    """Write offset requested by the central."""

    value: bytes = b""
    """Bytes written by the central."""


@dataclass
class PeripheralSubscriptionChangeEvent(ft.Event["BluetoothPeripheral"]):
    """Fired when a central subscribes or unsubscribes to notifications."""

    device_id: str
    """Central device whose subscription changed."""

    characteristic_uuid: str
    """UUID of the characteristic."""

    is_subscribed: bool = False
    """Whether the central is now subscribed."""

    # kw_only avoids clashing with Event.name in dataclass field ordering.
    name: Optional[str] = field(default=None, kw_only=True)
    """Optional central device name, when available."""


@dataclass
class PeripheralConnectionChangeEvent(ft.Event["BluetoothPeripheral"]):
    """Fired when a central connects to or disconnects from this peripheral."""

    device_id: str
    """Central device id."""

    connected: bool = False
    """Whether the central is now connected."""


@dataclass
class PeripheralAdvertisingStateChangeEvent(ft.Event["BluetoothPeripheral"]):
    """Fired when the advertising lifecycle state changes."""

    state: PeripheralAdvertisingState
    """New advertising state."""

    error: Optional[str] = None
    """Error message when ``state`` is :attr:`PeripheralAdvertisingState.ERROR`."""


@dataclass
class PeripheralMtuChangeEvent(ft.Event["BluetoothPeripheral"]):
    """Fired when the negotiated MTU with a central changes."""

    device_id: str
    """Central device id."""

    mtu: int = 0
    """New MTU value in bytes."""


@dataclass
class PeripheralServiceAddedEvent(ft.Event["BluetoothPeripheral"]):
    """Fired when a GATT service has been added (or failed to add)."""

    service_uuid: str
    """UUID of the service."""

    error: Optional[str] = None
    """Error message when the service could not be added."""
