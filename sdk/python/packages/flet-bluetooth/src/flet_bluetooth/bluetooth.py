"""BLE central/client service wrapping ``universal_ble``."""

from __future__ import annotations

from typing import Optional

import flet as ft
from flet.utils import from_dict
from flet_bluetooth.types import (BluetoothAndroidScanOptions,
                                  BluetoothAvailabilityChangeEvent,
                                  BluetoothAvailabilityState,
                                  BluetoothCharacteristicValueEvent,
                                  BluetoothConnectionChangeEvent,
                                  BluetoothConnectionPriority,
                                  BluetoothConnectionState, BluetoothDevice,
                                  BluetoothLogLevel,
                                  BluetoothPairingStateChangeEvent,
                                  BluetoothQueueType, BluetoothScanFilter,
                                  BluetoothScanResultEvent, BluetoothService,
                                  BluetoothSubscriptionType,
                                  BluetoothWebOptions, unwrap_bluetooth_result)

__all__ = ["Bluetooth"]


@ft.control("Bluetooth")
class Bluetooth(ft.Service):
    """
    A service for Bluetooth Low Energy (BLE) central/client operations.

    Add an instance to [`Page.services`][flet.Page.services] before calling methods.
    """

    queue_type: BluetoothQueueType = BluetoothQueueType.GLOBAL
    """
    How BLE commands are queued before execution.

    Defaults to :attr:`BluetoothQueueType.GLOBAL`.
    """

    command_timeout: Optional[ft.DurationValue] = None
    """
    Global timeout for BLE commands.

    ``None`` uses the upstream default (10 seconds).
    """

    log_level: BluetoothLogLevel = BluetoothLogLevel.NONE
    """
    Log verbosity for the underlying BLE implementation.

    Only effective in debug builds.
    """

    on_scan_result: Optional[ft.EventHandler[BluetoothScanResultEvent]] = None
    """Fires when a BLE device is discovered during a scan."""

    on_availability_change: Optional[
        ft.EventHandler[BluetoothAvailabilityChangeEvent]
    ] = None
    """Fires when Bluetooth adapter availability changes."""

    on_connection_change: Optional[ft.EventHandler[BluetoothConnectionChangeEvent]] = (
        None
    )
    """Fires when a device connection state changes."""

    on_characteristic_value: Optional[
        ft.EventHandler[BluetoothCharacteristicValueEvent]
    ] = None
    """Fires when a subscribed characteristic emits a new value."""

    on_pairing_state_change: Optional[
        ft.EventHandler[BluetoothPairingStateChangeEvent]
    ] = None
    """Fires when a device pairing state changes."""

    on_error: Optional[ft.ControlEventHandler["Bluetooth"]] = None
    """
    Fires when an asynchronous BLE error occurs.

    The :attr:`~flet.Event.data` property of the event handler argument
    contains information on the error.
    """

    async def get_availability_state(self) -> BluetoothAvailabilityState:
        """
        Get the current Bluetooth adapter availability state.

        Returns:
            The current :class:`BluetoothAvailabilityState`.

        Raises:
            BluetoothException: If the request fails.
        """
        r = unwrap_bluetooth_result(await self._invoke_method("get_availability_state"))
        return BluetoothAvailabilityState(r)

    async def enable(self) -> None:
        """
        Enable Bluetooth.

        Note:
            Not supported on Web or Apple platforms.

        Raises:
            BluetoothException: If enabling Bluetooth fails.
        """
        unwrap_bluetooth_result(await self._invoke_method("enable"))

    async def disable(self) -> None:
        """
        Disable Bluetooth.

        Note:
            Not supported on Web or Apple platforms.

        Raises:
            BluetoothException: If disabling Bluetooth fails.
        """
        unwrap_bluetooth_result(await self._invoke_method("disable"))

    async def request_permissions(
        self, *, with_android_fine_location: bool = False
    ) -> None:
        """
        Request platform Bluetooth (and optionally location) permissions.

        Args:
            with_android_fine_location: On Android 12+ (API 31+), also request
                fine location permission.

        Raises:
            BluetoothException: If permissions are denied.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "request_permissions",
                {"with_android_fine_location": with_android_fine_location},
            )
        )

    async def start_scan(
        self,
        *,
        scan_filter: Optional[BluetoothScanFilter] = None,
        android_options: Optional[BluetoothAndroidScanOptions] = None,
        web_options: Optional[BluetoothWebOptions] = None,
    ) -> None:
        """
        Start scanning for nearby BLE devices.

        Scan results arrive via :attr:`on_scan_result`.

        Args:
            scan_filter: Optional filter for services, name prefixes, and
                manufacturer data.
            android_options: Android-specific scan settings.
            web_options: Web Bluetooth request options.

        Raises:
            BluetoothException: If scanning cannot be started.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "start_scan",
                {
                    "scan_filter": scan_filter,
                    "android_options": android_options,
                    "web_options": web_options,
                },
            )
        )

    async def stop_scan(self) -> None:
        """
        Stop an active BLE scan.

        Raises:
            BluetoothException: If stopping the scan fails.
        """
        unwrap_bluetooth_result(await self._invoke_method("stop_scan"))

    async def is_scanning(self) -> bool:
        """
        Check whether a scan is currently active.

        Returns:
            ``True`` if scanning, otherwise ``False``.

        Raises:
            BluetoothException: If the request fails.
        """
        return bool(unwrap_bluetooth_result(await self._invoke_method("is_scanning")))

    async def get_system_devices(
        self, *, with_services: Optional[list[str]] = None
    ) -> list[BluetoothDevice]:
        """
        Get devices already connected to the system (by any app).

        Args:
            with_services: Optional service UUID filter. Required on Apple to
                return any devices.

        Returns:
            A list of :class:`BluetoothDevice` instances.

        Raises:
            BluetoothException: If the request fails.

        Note:
            Not supported on Web.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method(
                "get_system_devices",
                {"with_services": with_services},
            )
        )
        return [from_dict(BluetoothDevice, d) for d in (r or [])]

    async def connect(self, device_id: str, *, auto_connect: bool = False) -> None:
        """
        Connect to a remote BLE device.

        Args:
            device_id: Platform device identifier.
            auto_connect: When ``True``, automatically reconnect when the device
                becomes available (Android/Apple; ignored elsewhere).

        Raises:
            BluetoothException: If the connection fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "connect",
                {"device_id": device_id, "auto_connect": auto_connect},
            )
        )

    async def disconnect(self, device_id: str) -> None:
        """
        Disconnect from a remote BLE device.

        Args:
            device_id: Platform device identifier.

        Raises:
            BluetoothException: If disconnection fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method("disconnect", {"device_id": device_id})
        )

    async def is_connected(self, device_id: str) -> bool:
        """
        Check whether a device is currently connected.

        Args:
            device_id: Platform device identifier.

        Returns:
            ``True`` if connected, otherwise ``False``.

        Raises:
            BluetoothException: If the request fails.
        """
        return bool(
            unwrap_bluetooth_result(
                await self._invoke_method("is_connected", {"device_id": device_id})
            )
        )

    async def get_connection_state(self, device_id: str) -> BluetoothConnectionState:
        """
        Get the connection state of a device.

        Args:
            device_id: Platform device identifier.

        Returns:
            The current :class:`BluetoothConnectionState`.

        Raises:
            BluetoothException: If the request fails.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method("get_connection_state", {"device_id": device_id})
        )
        return BluetoothConnectionState(r)

    async def discover_services(self, device_id: str) -> list[BluetoothService]:
        """
        Discover GATT services on a connected device.

        Args:
            device_id: Platform device identifier.

        Returns:
            A list of discovered :class:`BluetoothService` instances.

        Raises:
            BluetoothException: If discovery fails.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method("discover_services", {"device_id": device_id})
        )
        return [from_dict(BluetoothService, s) for s in (r or [])]

    async def read_characteristic(
        self,
        device_id: str,
        service_uuid: str,
        characteristic_uuid: str,
    ) -> bytes:
        """
        Read a characteristic value.

        Args:
            device_id: Platform device identifier.
            service_uuid: Parent service UUID.
            characteristic_uuid: Characteristic UUID.

        Returns:
            The characteristic value as ``bytes``.

        Raises:
            BluetoothException: If the read fails.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method(
                "read_characteristic",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                },
            )
        )
        return b"" if r is None else bytes(r)

    async def write_characteristic(
        self,
        device_id: str,
        service_uuid: str,
        characteristic_uuid: str,
        value: bytes,
        *,
        with_response: bool = True,
    ) -> None:
        """
        Write a characteristic value.

        Args:
            device_id: Platform device identifier.
            service_uuid: Parent service UUID.
            characteristic_uuid: Characteristic UUID.
            value: Bytes to write.
            with_response: When ``True`` (default), write with response.

        Raises:
            BluetoothException: If the write fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "write_characteristic",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                    "value": value,
                    "with_response": with_response,
                },
            )
        )

    async def subscribe_characteristic(
        self,
        device_id: str,
        service_uuid: str,
        characteristic_uuid: str,
        *,
        subscription_type: BluetoothSubscriptionType = (
            BluetoothSubscriptionType.NOTIFICATIONS
        ),
    ) -> None:
        """
        Subscribe to characteristic notifications or indications.

        Updates arrive via :attr:`on_characteristic_value`.

        Args:
            device_id: Platform device identifier.
            service_uuid: Parent service UUID.
            characteristic_uuid: Characteristic UUID.
            subscription_type: Notification or indication mode.

        Raises:
            BluetoothException: If subscription fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "subscribe_characteristic",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                    "subscription_type": subscription_type,
                },
            )
        )

    async def unsubscribe_characteristic(
        self,
        device_id: str,
        service_uuid: str,
        characteristic_uuid: str,
    ) -> None:
        """
        Stop characteristic notifications/indications.

        Args:
            device_id: Platform device identifier.
            service_uuid: Parent service UUID.
            characteristic_uuid: Characteristic UUID.

        Raises:
            BluetoothException: If unsubscription fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "unsubscribe_characteristic",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                },
            )
        )

    async def pair(
        self,
        device_id: str,
        *,
        service_uuid: Optional[str] = None,
        characteristic_uuid: Optional[str] = None,
    ) -> None:
        """
        Pair with a device.

        Args:
            device_id: Platform device identifier.
            service_uuid: Encrypted characteristic's service UUID (required on
                Apple/Web for a reliable result).
            characteristic_uuid: Encrypted characteristic UUID (required on
                Apple/Web for a reliable result).

        Raises:
            BluetoothException: If pairing fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "pair",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                },
            )
        )

    async def unpair(self, device_id: str) -> None:
        """
        Unpair a device.

        Args:
            device_id: Platform device identifier.

        Raises:
            BluetoothException: If unpairing fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method("unpair", {"device_id": device_id})
        )

    async def is_paired(
        self,
        device_id: str,
        *,
        service_uuid: Optional[str] = None,
        characteristic_uuid: Optional[str] = None,
    ) -> Optional[bool]:
        """
        Check whether a device is paired.

        Args:
            device_id: Platform device identifier.
            service_uuid: Encrypted characteristic's service UUID (needed on
                Apple/Web).
            characteristic_uuid: Encrypted characteristic UUID (needed on
                Apple/Web).

        Returns:
            ``True``/``False`` when known, or ``None`` when the platform cannot
            determine pairing state without a pairing command.

        Raises:
            BluetoothException: If the request fails.
        """
        return unwrap_bluetooth_result(
            await self._invoke_method(
                "is_paired",
                {
                    "device_id": device_id,
                    "service_uuid": service_uuid,
                    "characteristic_uuid": characteristic_uuid,
                },
            )
        )

    async def request_mtu(self, device_id: str, mtu: int) -> int:
        """
        Request an MTU for the connection.

        Args:
            device_id: Platform device identifier.
            mtu: Desired MTU value.

        Returns:
            The negotiated MTU (may differ from ``mtu``).

        Raises:
            BluetoothException: If the request fails.
        """
        return int(
            unwrap_bluetooth_result(
                await self._invoke_method(
                    "request_mtu",
                    {"device_id": device_id, "mtu": mtu},
                )
            )
        )

    async def read_rssi(self, device_id: str) -> int:
        """
        Read the RSSI of a connected device.

        Args:
            device_id: Platform device identifier.

        Returns:
            RSSI in dBm.

        Raises:
            BluetoothException: If the read fails.
        """
        return int(
            unwrap_bluetooth_result(
                await self._invoke_method("read_rssi", {"device_id": device_id})
            )
        )

    async def request_connection_priority(
        self,
        device_id: str,
        priority: BluetoothConnectionPriority,
    ) -> None:
        """
        Request a connection priority update (Android only).

        Args:
            device_id: Platform device identifier.
            priority: Desired :class:`BluetoothConnectionPriority`.

        Raises:
            BluetoothException: If the request fails or is unsupported.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "request_connection_priority",
                {"device_id": device_id, "priority": priority},
            )
        )

    async def clear_queue(self, queue_id: Optional[str] = None) -> None:
        """
        Clear a BLE command queue.

        Args:
            queue_id: Queue to clear. Pass a device id for a per-device queue,
                or ``None`` to clear all queues.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "clear_queue",
                {"queue_id": queue_id},
            )
        )
