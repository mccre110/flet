import flet as ft

__all__ = ["BluetoothPeripheral"]


@ft.control("BluetoothPeripheral")
class BluetoothPeripheral(ft.Service):
    """
    A service for Bluetooth Low Energy (BLE) peripheral/server operations.

    Add an instance to [`Page.services`][flet.Page.services] before calling methods.
    """
