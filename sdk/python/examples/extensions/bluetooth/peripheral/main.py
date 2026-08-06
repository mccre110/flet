import asyncio

import flet as ft
import flet_bluetooth as fbt

# Standard Battery Service / Battery Level characteristic
BATTERY_SERVICE_UUID = "180f"
BATTERY_LEVEL_UUID = "2a19"


async def main(page: ft.Page):
    page.title = "Bluetooth peripheral"
    page.appbar = ft.AppBar(title=ft.Text("BLE battery peripheral"))

    status = ft.Text("Idle")
    level_text = ft.Text("Battery level: 100%")
    log = ft.Column(spacing=2, tight=True)
    level = [100]
    advertising = [False]

    def snack(message: str):
        page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    def append_log(message: str):
        log.controls.insert(0, ft.Text(message, size=12))
        del log.controls[20:]
        page.update()

    def on_characteristic_write(e: fbt.PeripheralCharacteristicWriteEvent):
        append_log(f"Write {e.characteristic_uuid}: {e.value!r} (offset={e.offset})")

    def on_characteristic_read(e: fbt.PeripheralCharacteristicReadEvent):
        append_log(f"Read {e.characteristic_uuid}: {e.value!r} (offset={e.offset})")

    def on_subscription_change(e: fbt.PeripheralSubscriptionChangeEvent):
        state = "subscribed" if e.is_subscribed else "unsubscribed"
        append_log(f"{e.device_id} {state} to {e.characteristic_uuid}")

    def on_connection_change(e: fbt.PeripheralConnectionChangeEvent):
        state = "connected" if e.connected else "disconnected"
        append_log(f"Central {e.device_id} {state}")

    def on_advertising_state_change(e: fbt.PeripheralAdvertisingStateChangeEvent):
        status.value = f"Advertising: {e.state.value}"
        page.update()
        if e.error:
            snack(e.error)

    def on_error(e):
        snack(f"Error: {e.data}")

    peri = fbt.BluetoothPeripheral(
        services=[
            fbt.GattService(
                uuid=BATTERY_SERVICE_UUID,
                characteristics=[
                    fbt.GattCharacteristic(
                        uuid=BATTERY_LEVEL_UUID,
                        properties=[
                            fbt.CharacteristicProperty.READ,
                            fbt.CharacteristicProperty.NOTIFY,
                        ],
                        permissions=[fbt.PeripheralAttributePermission.READABLE],
                        value=bytes([level[0]]),
                    )
                ],
            )
        ],
        on_characteristic_read=on_characteristic_read,
        on_characteristic_write=on_characteristic_write,
        on_subscription_change=on_subscription_change,
        on_connection_change=on_connection_change,
        on_advertising_state_change=on_advertising_state_change,
        on_error=on_error,
    )
    page.services.append(peri)

    async def check_capabilities(e: ft.Event[ft.Button]):
        try:
            caps = await peri.get_capabilities()
            status.value = f"Peripheral mode: {caps.supports_peripheral_mode}"
            snack(status.value)
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def start_advertising(e: ft.Event[ft.Button]):
        try:
            await peri.start_advertising(
                service_uuids=[BATTERY_SERVICE_UUID],
                local_name="Flet Battery",
            )
            advertising[0] = True
            status.value = "Advertising started"
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def stop_advertising(e: ft.Event[ft.Button]):
        try:
            await peri.stop_advertising()
            advertising[0] = False
            status.value = "Advertising stopped"
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def bump_level():
        while True:
            await asyncio.sleep(2)
            if not advertising[0]:
                continue
            level[0] = 100 if level[0] <= 5 else level[0] - 5
            level_text.value = f"Battery level: {level[0]}%"
            page.update()
            try:
                await peri.update_characteristic_value(
                    BATTERY_LEVEL_UUID,
                    bytes([level[0]]),
                )
            except fbt.BluetoothException as ex:
                append_log(str(ex))

    page.run_task(bump_level)

    page.add(
        ft.SafeArea(
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    status,
                    level_text,
                    ft.Text(
                        "Advertises the standard Battery Service (180F) with "
                        "Battery Level (2A19). The Flutter value cache answers "
                        "reads; Python updates the level periodically.",
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Row(
                        wrap=True,
                        controls=[
                            ft.Button(
                                "Capabilities",
                                on_click=check_capabilities,
                            ),
                            ft.Button(
                                "Start advertising",
                                on_click=start_advertising,
                            ),
                            ft.Button(
                                "Stop advertising",
                                on_click=stop_advertising,
                            ),
                        ],
                    ),
                    ft.Text("Event log", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Container(
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=10,
                        border_radius=8,
                        content=log,
                    ),
                ],
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
