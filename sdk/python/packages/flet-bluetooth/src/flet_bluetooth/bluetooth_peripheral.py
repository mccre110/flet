from dataclasses import field
from typing import Optional

import flet as ft
from flet.utils import from_dict
from flet_bluetooth.types import (
    GattService,
    PeripheralAdvertisingState,
    PeripheralAdvertisingStateChangeEvent,
    PeripheralAvailabilityState,
    PeripheralCapabilities,
    PeripheralCharacteristicReadEvent,
    PeripheralCharacteristicWriteEvent,
    PeripheralConnectionChangeEvent,
    PeripheralDescriptorReadEvent,
    PeripheralDescriptorWriteEvent,
    PeripheralManufacturerData,
    PeripheralMtuChangeEvent,
    PeripheralServiceAddedEvent,
    PeripheralSubscriptionChangeEvent,
    unwrap_bluetooth_result,
)

__all__ = ["BluetoothPeripheral"]


@ft.control("BluetoothPeripheral")
class BluetoothPeripheral(ft.Service):
    """
    A service for Bluetooth Low Energy (BLE) peripheral/server operations.

    Add an instance to [`Page.services`][flet.Page.services] before calling methods.

    Warning:
        GATT characteristic/descriptor **read requests are synchronous** on the
        native side (``universal_ble``'s ``OnPeripheralReadRequest`` returns a
        value immediately and cannot await Python). Flet control events are
        one-way, so Python cannot answer reads.

        The Flutter side therefore owns a **value cache** keyed by
        characteristic (and descriptor) UUID. Read handlers answer instantly
        from that cache (supporting ``offset`` slicing; empty bytes if missing).
        Write handlers update the cache, return success (or a GATT status for
        static rules such as not writable / value too long), then fire
        observational events to Python.

        Seed the cache by setting :attr:`services` characteristic/descriptor
        ``value`` fields, and keep it current with
        :meth:`update_characteristic_value`.

    Note:
        Only one :class:`BluetoothPeripheral` instance may be active at a time
        because ``universal_ble`` read/write request handlers are
        process-global.

        When :attr:`services` changes while advertising, advertising is stopped,
        services are cleared and re-added, and advertising is **not**
        automatically restarted.
    """

    services: list[GattService] = field(default_factory=list)
    """
    Declarative GATT service tree for this peripheral.

    On each update while not advertising, Dart syncs these services with the
    platform GATT server (clear + re-add) and seeds the value cache from each
    characteristic/descriptor ``value``. If advertising is active and
    ``services`` changes, advertising is stopped first, services are
    reconfigured, and advertising is left stopped.
    """

    on_characteristic_read: Optional[
        ft.EventHandler[PeripheralCharacteristicReadEvent]
    ] = None
    """
    Fires after Dart answered a characteristic read from the value cache.
    """

    on_characteristic_write: Optional[
        ft.EventHandler[PeripheralCharacteristicWriteEvent]
    ] = None
    """
    Fires after a characteristic write was accepted and cached.
    """

    on_descriptor_read: Optional[ft.EventHandler[PeripheralDescriptorReadEvent]] = None
    """
    Fires after Dart answered a descriptor read from the value cache.
    """

    on_descriptor_write: Optional[
        ft.EventHandler[PeripheralDescriptorWriteEvent]
    ] = None
    """
    Fires after a descriptor write was accepted and cached.
    """

    on_subscription_change: Optional[
        ft.EventHandler[PeripheralSubscriptionChangeEvent]
    ] = None
    """
    Fires when a central subscribes or unsubscribes to notifications/indications.
    """

    on_connection_change: Optional[
        ft.EventHandler[PeripheralConnectionChangeEvent]
    ] = None
    """
    Fires when a central connects to or disconnects from this peripheral.
    """

    on_advertising_state_change: Optional[
        ft.EventHandler[PeripheralAdvertisingStateChangeEvent]
    ] = None
    """
    Fires when the advertising lifecycle state changes.
    """

    on_mtu_change: Optional[ft.EventHandler[PeripheralMtuChangeEvent]] = None
    """
    Fires when the negotiated MTU with a central changes.
    """

    on_service_added: Optional[ft.EventHandler[PeripheralServiceAddedEvent]] = None
    """
    Fires when a GATT service has been added (or failed to add).
    """

    on_error: Optional[ft.ControlEventHandler["BluetoothPeripheral"]] = None
    """
    Fires when an asynchronous peripheral error occurs.

    The :attr:`~flet.Event.data` property of the event handler argument contains
    information on the error.
    """

    async def get_capabilities(self) -> PeripheralCapabilities:
        """
        Returns platform capabilities for BLE peripheral mode.

        Returns:
            A :class:`~flet_bluetooth.PeripheralCapabilities` snapshot.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method("get_capabilities")
        )
        return from_dict(PeripheralCapabilities, r or {})

    async def get_availability_state(self) -> PeripheralAvailabilityState:
        """
        Returns the peripheral readiness / availability state.

        Returns:
            A :class:`~flet_bluetooth.PeripheralAvailabilityState` value.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method("get_availability_state")
        )
        return PeripheralAvailabilityState(r)

    async def get_advertising_state(self) -> PeripheralAdvertisingState:
        """
        Returns the current advertising lifecycle state.

        Returns:
            A :class:`~flet_bluetooth.PeripheralAdvertisingState` value.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method("get_advertising_state")
        )
        return PeripheralAdvertisingState(r)

    async def start_advertising(
        self,
        *,
        service_uuids: Optional[list[str]] = None,
        local_name: Optional[str] = None,
        manufacturer_data: Optional[PeripheralManufacturerData] = None,
        timeout: Optional[ft.DurationValue] = None,
    ) -> None:
        """
        Starts BLE advertising.

        Args:
            service_uuids: Service UUIDs to advertise. When ``None``, UUIDs from
                :attr:`services` are used.
            local_name: Local name included in the advertisement when supported.
                On Windows this is rejected by the platform stack.
            manufacturer_data: Optional manufacturer-specific advertisement data.
                On Windows this is rejected by the platform stack.
            timeout: Optional advertising timeout when supported by the platform.

        Raises:
            BluetoothException: If advertising cannot be started.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "start_advertising",
                arguments={
                    "service_uuids": service_uuids,
                    "local_name": local_name,
                    "manufacturer_data": manufacturer_data,
                    "timeout": timeout,
                },
            )
        )

    async def stop_advertising(self) -> None:
        """
        Stops BLE advertising.

        Raises:
            BluetoothException: If advertising cannot be stopped.
        """
        unwrap_bluetooth_result(await self._invoke_method("stop_advertising"))

    async def update_characteristic_value(
        self,
        characteristic_uuid: str,
        value: bytes,
        *,
        device_id: Optional[str] = None,
    ) -> None:
        """
        Updates a characteristic value in the Dart cache and notifies subscribers.

        Args:
            characteristic_uuid: UUID of the characteristic to update.
            value: New value bytes.
            device_id: Optional central device id to target when the platform
                supports targeted updates; otherwise all subscribers are notified.

        Raises:
            BluetoothException: If the update fails.
        """
        unwrap_bluetooth_result(
            await self._invoke_method(
                "update_characteristic_value",
                arguments={
                    "characteristic_uuid": characteristic_uuid,
                    "value": value,
                    "device_id": device_id,
                },
            )
        )

    async def get_subscribed_clients(self, characteristic_uuid: str) -> list[str]:
        """
        Returns device ids currently subscribed to a characteristic.

        Args:
            characteristic_uuid: UUID of the characteristic.

        Returns:
            A list of central device ids.
        """
        r = unwrap_bluetooth_result(
            await self._invoke_method(
                "get_subscribed_clients",
                arguments={"characteristic_uuid": characteristic_uuid},
            )
        )
        return list(r or [])

    async def get_maximum_notify_length(self, device_id: str) -> Optional[int]:
        """
        Returns the maximum notification payload length for a connected central.

        Args:
            device_id: Central device id.

        Returns:
            Maximum notify length in bytes, or ``None`` if unknown/unsupported.
        """
        return unwrap_bluetooth_result(
            await self._invoke_method(
                "get_maximum_notify_length",
                arguments={"device_id": device_id},
            )
        )
