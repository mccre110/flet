import asyncio

import flet as ft
import flet_bluetooth as fbt


async def main(page: ft.Page):
    page.title = "Bluetooth scanner"
    page.appbar = ft.AppBar(title=ft.Text("BLE scanner"))

    status = ft.Text("Idle")
    devices_list = ft.Column(spacing=4, tight=True)
    services_list = ft.Column(spacing=4, tight=True)
    discovered: dict[str, fbt.BluetoothDevice] = {}
    selected_id: list[str | None] = [None]
    render_scheduled = False

    def snack(message: str):
        page.show_dialog(ft.SnackBar(content=ft.Text(message)))

    def render_devices():
        devices_list.controls.clear()
        for device in sorted(
            discovered.values(),
            key=lambda d: (d.name or "", d.device_id),
        ):
            label = device.name or "(unnamed)"
            rssi = f"{device.rssi} dBm" if device.rssi is not None else "n/a"
            devices_list.controls.append(
                ft.Container(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    padding=10,
                    border_radius=8,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                tight=True,
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(label, weight=ft.FontWeight.W_600),
                                    ft.Text(
                                        f"{device.device_id} · RSSI {rssi}",
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                            ),
                            ft.Button(
                                "Connect",
                                on_click=lambda e, did=device.device_id: page.run_task(
                                    connect_device, did
                                ),
                            ),
                        ],
                    ),
                )
            )

    async def flush_devices():
        nonlocal render_scheduled
        await asyncio.sleep(0.2)
        render_scheduled = False
        render_devices()

    def on_scan_result(e: fbt.BluetoothScanResultEvent):
        nonlocal render_scheduled
        discovered[e.device.device_id] = e.device
        if not render_scheduled:
            render_scheduled = True
            page.run_task(flush_devices)


    def on_connection_change(e: fbt.BluetoothConnectionChangeEvent):
        state = "connected" if e.is_connected else "disconnected"
        status.value = f"{e.device_id}: {state}"
        if e.error:
            snack(e.error)

    def on_error(e):
        snack(f"Error: {e.data}")

    bt = fbt.Bluetooth(
        on_scan_result=on_scan_result,
        on_connection_change=on_connection_change,
        on_error=on_error,
    )
    page.services.append(bt)

    async def request_permissions(e: ft.Event[ft.Button]):
        try:
            await bt.request_permissions()
            status.value = "Permissions granted"
            snack("Permissions granted")
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def check_availability(e: ft.Event[ft.Button]):
        try:
            state = await bt.get_availability_state()
            status.value = f"Availability: {state.value}"
            snack(status.value)
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def start_scan(e: ft.Event[ft.Button]):
        try:
            discovered.clear()
            render_devices()
            services_list.controls.clear()
            await bt.start_scan()
            status.value = "Scanning…"
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def stop_scan(e: ft.Event[ft.Button]):
        try:
            await bt.stop_scan()
            status.value = "Scan stopped"
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def connect_device(device_id: str):
        selected_id[0] = device_id
        services_list.controls.clear()
        try:
            await bt.stop_scan()
        except fbt.BluetoothException:
            pass
        try:
            status.value = f"Connecting to {device_id}…"
            await bt.connect(device_id)
            services = await bt.discover_services(device_id)
            for service in services:
                chars = ", ".join(c.uuid for c in service.characteristics) or "(none)"
                services_list.controls.append(
                    ft.Container(
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        padding=10,
                        border_radius=8,
                        content=ft.Column(
                            tight=True,
                            spacing=2,
                            controls=[
                                ft.Text(
                                    f"Service {service.uuid}",
                                    weight=ft.FontWeight.W_600,
                                ),
                                ft.Text(
                                    f"Characteristics: {chars}",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                            ],
                        ),
                    )
                )
            status.value = f"Connected · {len(services)} service(s)"
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    async def disconnect(e: ft.Event[ft.Button]):
        device_id = selected_id[0]
        if not device_id:
            snack("No device selected")
            return
        try:
            await bt.disconnect(device_id)
            status.value = "Disconnected"
            services_list.controls.clear()
        except fbt.BluetoothException as ex:
            status.value = str(ex)
            snack(str(ex))

    page.add(
        ft.SafeArea(
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
                controls=[
                    status,
                    ft.Row(
                        wrap=True,
                        controls=[
                            ft.Button(
                                "Request permissions",
                                on_click=request_permissions,
                            ),
                            ft.Button(
                                "Availability",
                                on_click=check_availability,
                            ),
                            ft.Button("Start scan", on_click=start_scan),
                            ft.Button("Stop scan", on_click=stop_scan),
                            ft.Button("Disconnect", on_click=disconnect),
                        ],
                    ),
                    ft.Text("Devices", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    devices_list,
                    ft.Text("Services", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    services_list,
                ],
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)
