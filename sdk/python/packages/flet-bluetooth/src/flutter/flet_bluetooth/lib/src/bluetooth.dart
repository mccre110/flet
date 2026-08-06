import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';

class BluetoothService extends FletService {
  BluetoothService({required super.control});

  @override
  void init() {
    super.init();
    debugPrint("Bluetooth(${control.id}).init: ${control.properties}");
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("Bluetooth.$name($args)");
    switch (name) {
      default:
        throw Exception("Unknown Bluetooth method: $name");
    }
  }

  @override
  void dispose() {
    debugPrint("Bluetooth(${control.id}).dispose()");
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}
