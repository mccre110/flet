import 'dart:async';
import 'dart:typed_data';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:universal_ble/universal_ble.dart';

import 'utils/bluetooth.dart';

class _UnknownBluetoothMethod implements Exception {
  final String name;
  const _UnknownBluetoothMethod(this.name);

  @override
  String toString() => "Unknown Bluetooth method: $name";
}

class BluetoothService extends FletService {
  BluetoothService({required super.control});

  StreamSubscription<BleDevice>? _scanSubscription;
  StreamSubscription<AvailabilityState>? _availabilitySubscription;
  final Map<String, StreamSubscription<bool>> _connectionSubscriptions = {};
  final Map<String, StreamSubscription<bool>> _pairingSubscriptions = {};
  final Map<String, StreamSubscription<Uint8List>>
      _characteristicSubscriptions = {};

  /// Devices we explicitly care about for connection/pairing streams.
  /// Scan sightings are not tracked here — that set would grow unbounded.
  final Set<String> _trackedDevices = {};

  /// Whether this service instance started the process-global scan.
  bool _ownsScan = false;

  QueueType? _appliedQueueType;
  Duration? _appliedTimeout;
  BleLogLevel? _appliedLogLevel;
  bool? _wantScan;
  bool? _wantAvailability;
  bool? _wantConnection;
  bool? _wantPairing;

  @override
  void init() {
    super.init();
    debugPrint("Bluetooth(${control.id}).init: ${control.properties}");
    control.addInvokeMethodListener(_invokeMethod);
    applySettings();
    registerEvents();
  }

  @override
  void update() {
    debugPrint("Bluetooth(${control.id}).update: ${control.properties}");
    applySettings();
    registerEvents();
  }

  void applySettings() {
    final queueType = parseEnum(
      QueueType.values,
      control.getString("queue_type"),
      QueueType.global,
    )!;
    if (_appliedQueueType != queueType) {
      UniversalBle.queueType = queueType;
      _appliedQueueType = queueType;
    }

    // Python None => upstream default of 10 seconds.
    final timeout = control.getDuration(
      "command_timeout",
      const Duration(seconds: 10),
    );
    if (_appliedTimeout != timeout) {
      UniversalBle.timeout = timeout;
      _appliedTimeout = timeout;
    }

    final logLevel = parseEnum(
      BleLogLevel.values,
      control.getString("log_level"),
      BleLogLevel.none,
    )!;
    if (_appliedLogLevel != logLevel) {
      unawaited(UniversalBle.setLogLevel(logLevel));
      _appliedLogLevel = logLevel;
    }
  }

  void registerEvents() {
    final wantScan = control.hasEventHandler("scan_result");
    final wantAvailability = control.hasEventHandler("availability_change");
    final wantConnection = control.hasEventHandler("connection_change");
    final wantPairing = control.hasEventHandler("pairing_state_change");

    if (_wantScan != wantScan) {
      _scanSubscription?.cancel();
      _scanSubscription = null;
      if (wantScan) {
        _scanSubscription = UniversalBle.scanStream.listen(
          (device) {
            control.triggerEvent("scan_result", {
              "device": bleDeviceToMap(device),
            });
          },
          onError: (Object error) {
            control.triggerEvent("error", error.toString());
          },
        );
      }
      _wantScan = wantScan;
    }

    if (_wantAvailability != wantAvailability) {
      _availabilitySubscription?.cancel();
      _availabilitySubscription = null;
      if (wantAvailability) {
        _availabilitySubscription = UniversalBle.availabilityStream.listen(
          (state) {
            control.triggerEvent("availability_change", {
              "state": state.name,
            });
          },
          onError: (Object error) {
            control.triggerEvent("error", error.toString());
          },
        );
      }
      _wantAvailability = wantAvailability;
    }

    if (_wantConnection != wantConnection || _wantPairing != wantPairing) {
      _wantConnection = wantConnection;
      _wantPairing = wantPairing;
      _resyncDeviceSubscriptions();
    }
  }

  void _resyncDeviceSubscriptions() {
    for (final sub in _connectionSubscriptions.values) {
      sub.cancel();
    }
    _connectionSubscriptions.clear();
    for (final sub in _pairingSubscriptions.values) {
      sub.cancel();
    }
    _pairingSubscriptions.clear();

    final listenConnection = _wantConnection == true;
    final listenPairing = _wantPairing == true;
    if (!listenConnection && !listenPairing) {
      return;
    }

    for (final deviceId in _trackedDevices) {
      _listenDevice(deviceId);
    }
  }

  void _listenDevice(String deviceId) {
    if (_wantConnection == true &&
        !_connectionSubscriptions.containsKey(deviceId)) {
      _connectionSubscriptions[deviceId] =
          UniversalBle.connectionStream(deviceId).listen(
        (isConnected) {
          control.triggerEvent("connection_change", {
            "device_id": deviceId,
            "is_connected": isConnected,
            "state": isConnected
                ? BleConnectionState.connected.name
                : BleConnectionState.disconnected.name,
          });
        },
        onError: (Object error) {
          control.triggerEvent("error", error.toString());
        },
      );
    }
    if (_wantPairing == true && !_pairingSubscriptions.containsKey(deviceId)) {
      _pairingSubscriptions[deviceId] =
          UniversalBle.pairingStateStream(deviceId).listen(
        (isPaired) {
          control.triggerEvent("pairing_state_change", {
            "device_id": deviceId,
            "is_paired": isPaired,
          });
        },
        onError: (Object error) {
          control.triggerEvent("error", error.toString());
        },
      );
    }
  }

  void _trackDevice(String deviceId) {
    if (_trackedDevices.add(deviceId)) {
      _listenDevice(deviceId);
    }
  }

  String _charKey(String deviceId, String characteristicUuid) =>
      "$deviceId|${characteristicUuid.toLowerCase()}";

  void _listenCharacteristicValue(
    String deviceId,
    String serviceUuid,
    String characteristicUuid,
  ) {
    final key = _charKey(deviceId, characteristicUuid);
    _characteristicSubscriptions[key]?.cancel();
    _characteristicSubscriptions[key] =
        UniversalBle.characteristicValueStream(deviceId, characteristicUuid)
            .listen(
      (value) {
        control.triggerEvent("characteristic_value", {
          "device_id": deviceId,
          "service_uuid": serviceUuid,
          "characteristic_uuid": characteristicUuid,
          "value": value,
        });
      },
      onError: (Object error) {
        control.triggerEvent("error", error.toString());
      },
    );
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("Bluetooth.$name($args)");
    try {
      switch (name) {
        case "get_availability_state":
          final state = await UniversalBle.getBluetoothAvailabilityState();
          return okResult(state.name);

        case "enable":
          await UniversalBle.enableBluetooth();
          return okResult();

        case "disable":
          await UniversalBle.disableBluetooth();
          return okResult();

        case "request_permissions":
          await UniversalBle.requestPermissions(
            withAndroidFineLocation:
                parseBool(args?["with_android_fine_location"], false)!,
          );
          return okResult();

        case "start_scan":
          await UniversalBle.startScan(
            scanFilter: parseScanFilter(args?["scan_filter"]),
            platformConfig: parsePlatformConfig(
              androidOptions: args?["android_options"],
              webOptions: args?["web_options"],
            ),
          );
          _ownsScan = true;
          return okResult();

        case "stop_scan":
          await UniversalBle.stopScan();
          _ownsScan = false;
          return okResult();

        case "is_scanning":
          return okResult(await UniversalBle.isScanning());

        case "get_system_devices":
          final withServices =
              (args?["with_services"] as List?)?.cast<String>();
          final devices = await UniversalBle.getSystemDevices(
            withServices: withServices,
          );
          for (final device in devices) {
            _trackDevice(device.deviceId);
          }
          return okResult(devices.map(bleDeviceToMap).toList());

        case "connect":
          final deviceId = args["device_id"] as String;
          _trackDevice(deviceId);
          await UniversalBle.connect(
            deviceId,
            autoConnect: parseBool(args?["auto_connect"], false)!,
          );
          return okResult();

        case "disconnect":
          final deviceId = args["device_id"] as String;
          await UniversalBle.disconnect(deviceId);
          return okResult();

        case "is_connected":
          final state = await UniversalBle.getConnectionState(
            args["device_id"] as String,
          );
          return okResult(state == BleConnectionState.connected);

        case "get_connection_state":
          final state = await UniversalBle.getConnectionState(
            args["device_id"] as String,
          );
          return okResult(state.name);

        case "discover_services":
          final services = await UniversalBle.discoverServices(
            args["device_id"] as String,
          );
          return okResult(services.map(bleServiceToMap).toList());

        case "read_characteristic":
          final value = await UniversalBle.read(
            args["device_id"] as String,
            args["service_uuid"] as String,
            args["characteristic_uuid"] as String,
          );
          return okResult(value);

        case "write_characteristic":
          await UniversalBle.write(
            args["device_id"] as String,
            args["service_uuid"] as String,
            args["characteristic_uuid"] as String,
            parseBytes(args["value"]),
            withoutResponse: !parseBool(args?["with_response"], true)!,
          );
          return okResult();

        case "subscribe_characteristic":
          {
            final deviceId = args["device_id"] as String;
            final serviceUuid = args["service_uuid"] as String;
            final characteristicUuid = args["characteristic_uuid"] as String;
            final typeName = (args?["subscription_type"] as String?) ??
                "notifications";
            _trackDevice(deviceId);
            if (typeName.toLowerCase() == "indications") {
              await UniversalBle.subscribeIndications(
                deviceId,
                serviceUuid,
                characteristicUuid,
              );
            } else {
              await UniversalBle.subscribeNotifications(
                deviceId,
                serviceUuid,
                characteristicUuid,
              );
            }
            _listenCharacteristicValue(
              deviceId,
              serviceUuid,
              characteristicUuid,
            );
            return okResult();
          }

        case "unsubscribe_characteristic":
          {
            final deviceId = args["device_id"] as String;
            final serviceUuid = args["service_uuid"] as String;
            final characteristicUuid = args["characteristic_uuid"] as String;
            await UniversalBle.unsubscribe(
              deviceId,
              serviceUuid,
              characteristicUuid,
            );
            final key = _charKey(deviceId, characteristicUuid);
            await _characteristicSubscriptions.remove(key)?.cancel();
            return okResult();
          }

        case "pair":
          {
            final deviceId = args["device_id"] as String;
            _trackDevice(deviceId);
            await UniversalBle.pair(
              deviceId,
              pairingCommand: parsePairingCommand(args),
            );
            return okResult();
          }

        case "unpair":
          await UniversalBle.unpair(args["device_id"] as String);
          return okResult();

        case "is_paired":
          {
            final deviceId = args["device_id"] as String;
            final paired = await UniversalBle.isPaired(
              deviceId,
              pairingCommand: parsePairingCommand(args),
            );
            return okResult(paired);
          }

        case "request_mtu":
          {
            final mtu = await UniversalBle.requestMtu(
              args["device_id"] as String,
              (args["mtu"] as num).toInt(),
            );
            return okResult(mtu);
          }

        case "read_rssi":
          {
            final rssi =
                await UniversalBle.readRssi(args["device_id"] as String);
            return okResult(rssi);
          }

        case "request_connection_priority":
          {
            final priority = parseEnum(
              BleConnectionPriority.values,
              args["priority"] as String?,
              BleConnectionPriority.balanced,
            )!;
            await UniversalBle.requestConnectionPriority(
              args["device_id"] as String,
              priority,
            );
            return okResult();
          }

        case "clear_queue":
          UniversalBle.clearQueue(args?["queue_id"] as String?);
          return okResult();

        default:
          throw _UnknownBluetoothMethod(name);
      }
    } on _UnknownBluetoothMethod {
      rethrow;
    } catch (error) {
      return errorResult(error);
    }
  }

  @override
  void dispose() {
    debugPrint("Bluetooth(${control.id}).dispose()");
    _scanSubscription?.cancel();
    _availabilitySubscription?.cancel();
    for (final sub in _connectionSubscriptions.values) {
      sub.cancel();
    }
    _connectionSubscriptions.clear();
    for (final sub in _pairingSubscriptions.values) {
      sub.cancel();
    }
    _pairingSubscriptions.clear();
    for (final sub in _characteristicSubscriptions.values) {
      sub.cancel();
    }
    _characteristicSubscriptions.clear();
    _trackedDevices.clear();
    // stopScan is process-global — only stop if this instance started it.
    if (_ownsScan) {
      _ownsScan = false;
      unawaited(UniversalBle.stopScan().catchError((Object e) {
        debugPrint("Bluetooth.stopScan on dispose: $e");
      }));
    }
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}
