import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/telemetry_model.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final _packetController = StreamController<TelemetryPacket>.broadcast();
  bool _isConnected = false;
  String? _currentAssetId;

  Stream<TelemetryPacket> get packetStream => _packetController.stream;
  bool get isConnected => _isConnected;

  void connect(String assetId) {
    if (_currentAssetId == assetId && _isConnected) return;
    disconnect();

    _currentAssetId = assetId;
    final wsUrl = Uri.parse('ws://localhost:8000/api/v1/telemetry/ws/$assetId');

    try {
      _channel = WebSocketChannel.connect(wsUrl);
      _isConnected = true;

      _channel!.stream.listen(
        (dynamic message) {
          try {
            final Map<String, dynamic> data = jsonDecode(message.toString());
            final packet = TelemetryPacket.fromJson(data);
            _packetController.add(packet);
          } catch (e) {
            // Decoding error
          }
        },
        onError: (error) {
          _isConnected = false;
        },
        onDone: () {
          _isConnected = false;
        },
      );
    } catch (e) {
      _isConnected = false;
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
    _currentAssetId = null;
  }

  void dispose() {
    disconnect();
    _packetController.close();
  }
}
