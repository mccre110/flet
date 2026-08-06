import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';

class BluetoothPeripheralService extends FletService {
  BluetoothPeripheralService({required super.control});

  @override
  void init() {
    super.init();
    debugPrint(
        "BluetoothPeripheral(${control.id}).init: ${control.properties}");
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("BluetoothPeripheral.$name($args)");
    switch (name) {
      default:
        throw Exception("Unknown BluetoothPeripheral method: $name");
    }
  }

  @override
  void dispose() {
    debugPrint("BluetoothPeripheral(${control.id}).dispose()");
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}
