import flet as ft

__all__ = ["Bluetooth"]


@ft.control("Bluetooth")
class Bluetooth(ft.Service):
    """
    A service for Bluetooth Low Energy (BLE) central/client operations.

    Add an instance to [`Page.services`][flet.Page.services] before calling methods.
    """
