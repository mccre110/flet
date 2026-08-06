# flet-bluetooth

[![pypi](https://img.shields.io/pypi/v/flet-bluetooth.svg)](https://pypi.python.org/pypi/flet-bluetooth)
[![downloads](https://static.pepy.tech/badge/flet-bluetooth/month)](https://pepy.tech/project/flet-bluetooth)
[![python](https://img.shields.io/badge/python-%3E%3D3.10-%2334D058)](https://pypi.org/project/flet-bluetooth)
[![docstring coverage](https://flet.dev/docs/assets/badges/docs-coverage/flet-bluetooth.svg)](https://flet.dev/docs/assets/badges/docs-coverage/flet-bluetooth.svg)
[![license](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://github.com/flet-dev/flet/blob/main/sdk/python/packages/flet-bluetooth/LICENSE)

Adds Bluetooth Low Energy (BLE) capabilities to your [Flet](https://flet.dev) apps.

It is based on the [universal_ble](https://pub.dev/packages/universal_ble) Flutter package
(BSD-3-Clause). Classic Bluetooth is not supported.

| Service | Role |
|---------|------|
| `Bluetooth` | Central / client — scan, connect, GATT |
| `BluetoothPeripheral` | Peripheral / server — advertise, GATT server |

> **Important:** Add `Bluetooth` / `BluetoothPeripheral` instances to `page.services` before calling methods.
>
> Only one `BluetoothPeripheral` instance may be active at a time.

## Documentation

Detailed documentation to this package can be found [here](https://flet.dev/docs/services/bluetooth/).

## Platform Support

### Bluetooth (central)

| Platform | Windows | macOS | Linux | iOS | Android | Web |
|----------|---------|-------|-------|-----|---------|-----|
| Supported|    ✅    |   ✅   |   ✅   |  ✅  |    ✅    |  ⚠️  |

### BluetoothPeripheral

| Platform | Windows | macOS | Linux | iOS | Android | Web |
|----------|---------|-------|-------|-----|---------|-----|
| Supported|    ✅    |   ✅   |   ⚠️   |  ✅  |    ✅    |  ❌  |

Web Bluetooth (central) typically requires a user gesture. Linux peripheral support
depends on upstream completeness.

## Usage

### Installation

To install the `flet-bluetooth` package and add it to your project dependencies:

- Using `uv`:
    ```bash
    uv add flet-bluetooth
    ```

- Using `pip`:
    ```bash
    pip install flet-bluetooth
    ```
    After this, you will have to manually add this package to your `requirements.txt` or `pyproject.toml`.

When packaging with `flet build`, declare Bluetooth permissions via the predefined bundle:

```bash
flet build <target_platform> --permissions bluetooth
```

or in `pyproject.toml`:

```toml
[tool.flet]
permissions = ["bluetooth"]
```

### Examples

For examples, see [these](https://github.com/flet-dev/flet/tree/main/sdk/python/examples/extensions/bluetooth).
