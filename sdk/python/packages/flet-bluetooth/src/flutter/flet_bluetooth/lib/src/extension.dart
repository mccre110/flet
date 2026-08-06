import 'package:flet/flet.dart';

import 'bluetooth.dart';
import 'bluetooth_peripheral.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "Bluetooth":
        return BluetoothService(control: control);
      case "BluetoothPeripheral":
        return BluetoothPeripheralService(control: control);
      default:
        return null;
    }
  }
}
