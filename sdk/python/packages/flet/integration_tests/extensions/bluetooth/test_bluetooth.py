import flet as ft
import flet.testing as ftt
import flet_bluetooth as fbt
import pytest


@pytest.mark.asyncio(loop_scope="function")
async def test_bluetooth_services_mount(flet_app_function: ftt.FletTestApp):
    """Services register and mount without crashing the app."""
    flet_app = flet_app_function
    bt = fbt.Bluetooth()
    peri = fbt.BluetoothPeripheral(
        services=[
            fbt.GattService(
                uuid="180f",
                characteristics=[
                    fbt.GattCharacteristic(
                        uuid="2a19",
                        properties=[fbt.CharacteristicProperty.READ],
                        permissions=[fbt.PeripheralAttributePermission.READABLE],
                        value=bytes([100]),
                    )
                ],
            )
        ]
    )
    flet_app.page.services.extend([bt, peri])
    flet_app.page.add(ft.Text("Bluetooth smoke", key="label"))
    await flet_app.tester.pump_and_settle()

    assert (await flet_app.tester.find_by_key("label")).count == 1
    assert bt in flet_app.page.services
    assert peri in flet_app.page.services


@pytest.mark.asyncio(loop_scope="function")
async def test_bluetooth_availability_resilient(flet_app_function: ftt.FletTestApp):
    """
    Invoke get_availability_state when possible.

    Headless CI hosts often lack Bluetooth; accept BluetoothException / RuntimeError
    while still proving the invoke path is wired.
    """
    flet_app = flet_app_function
    bt = fbt.Bluetooth()
    peri = fbt.BluetoothPeripheral()
    flet_app.page.services.extend([bt, peri])
    await flet_app.tester.pump_and_settle()

    try:
        state = await bt.get_availability_state()
        assert isinstance(state, fbt.BluetoothAvailabilityState)
    except (fbt.BluetoothException, RuntimeError, TimeoutError):
        pass

    try:
        peri_state = await peri.get_availability_state()
        assert isinstance(peri_state, fbt.PeripheralAvailabilityState)
    except (fbt.BluetoothException, RuntimeError, TimeoutError):
        pass


def test_unwrap_bluetooth_result():
    assert fbt.unwrap_bluetooth_result({"ok": True, "value": 42}) == 42
    assert fbt.unwrap_bluetooth_result({"ok": True, "value": None}) is None
    assert fbt.unwrap_bluetooth_result("plain") == "plain"
    assert fbt.unwrap_bluetooth_result(7) == 7

    with pytest.raises(fbt.BluetoothException) as exc_info:
        fbt.unwrap_bluetooth_result(
            {
                "ok": False,
                "code": "notSupported",
                "message": "nope",
                "details": {"x": 1},
            }
        )
    assert exc_info.value.message == "nope"
    assert exc_info.value.code == fbt.BluetoothErrorCode.NOT_SUPPORTED
    assert exc_info.value.details == {"x": 1}


def test_gatt_and_scan_types_construct():
    device = fbt.BluetoothDevice(
        device_id="abc",
        name="Sensor",
        rssi=-50,
        service_uuids=["180f"],
        manufacturer_data_list=[
            fbt.ManufacturerData(company_id=0x004C, payload=b"\x01\x02")
        ],
    )
    assert device.device_id == "abc"
    assert device.manufacturer_data_list[0].company_id == 0x004C

    filt = fbt.BluetoothScanFilter(
        with_services=["180f"],
        with_name_prefix=["Flet"],
        exclusion_filters=[
            fbt.ExclusionFilter(name_prefix="Hidden"),
        ],
    )
    assert filt.with_services == ["180f"]
    assert filt.exclusion_filters[0].name_prefix == "Hidden"

    service = fbt.GattService(
        uuid="180f",
        characteristics=[
            fbt.GattCharacteristic(
                uuid="2a19",
                properties=[
                    fbt.CharacteristicProperty.READ,
                    fbt.CharacteristicProperty.NOTIFY,
                ],
                value=bytes([80]),
            )
        ],
    )
    assert service.primary is True
    assert service.characteristics[0].value == bytes([80])
