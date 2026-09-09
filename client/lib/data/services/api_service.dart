import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../models/asset_model.dart';
import '../models/telemetry_model.dart';
import '../models/visual_inspection_model.dart';
import '../models/work_order_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';

  Future<List<CivilAssetModel>> getAssets() async {
    final response = await http.get(Uri.parse('$baseUrl/api/v1/assets/'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => CivilAssetModel.fromJson(e)).toList();
    }
    throw Exception('Failed to fetch assets: ${response.statusCode}');
  }

  Future<Map<String, dynamic>> getAssetInstrumentation(String assetId) async {
    final response = await http.get(Uri.parse('$baseUrl/api/v1/assets/$assetId/instrumentation'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to fetch instrumentation: ${response.statusCode}');
  }

  Future<List<TelemetryReading>> getSampleTelemetry(String assetId) async {
    final response = await http.get(Uri.parse('$baseUrl/api/v1/telemetry/sample-stream/$assetId'));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> readings = data['readings'] ?? [];
      return readings.map((e) => TelemetryReading.fromJson(e)).toList();
    }
    throw Exception('Failed to fetch sample telemetry');
  }

  Future<VisualInspectionResult> uploadVisualInspection(
      Uint8List imageBytes, String filename) async {
    final uri = Uri.parse('$baseUrl/api/v1/prediction/visual-inspection');
    final request = http.MultipartRequest('POST', uri);

    final multipartFile = http.MultipartFile.fromBytes(
      'file',
      imageBytes,
      filename: filename,
      contentType: MediaType('image', 'png'),
    );
    request.files.add(multipartFile);

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return VisualInspectionResult.fromJson(data);
    }
    throw Exception('Visual inspection failed: ${response.statusCode} - ${response.body}');
  }

  Future<WorkOrderModel> evaluateDecision({
    required String assetId,
    required int predictedClass,
    required List<double> classProbabilities,
    required double maxStrain,
    required double maxVibration,
    required double crackPropagationMm,
    required String roadClass,
    required double importanceWeight,
  }) async {
    final uri = Uri.parse('$baseUrl/api/v1/decision/evaluate');
    final payload = {
      'asset_id': assetId,
      'predicted_class': predictedClass,
      'class_probabilities': classProbabilities,
      'telemetry_summary': {
        'max_strain': maxStrain,
        'max_vibration': maxVibration,
        'crack_propagation_mm': crackPropagationMm,
      },
      'road_class': roadClass,
      'importance_weight': importanceWeight,
    };

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return WorkOrderModel.fromJson(data['work_order'] ?? {});
    }
    throw Exception('Failed to evaluate IDSS decision: ${response.statusCode}');
  }

  Future<List<WorkOrderModel>> getWorkOrders() async {
    final response = await http.get(Uri.parse('$baseUrl/api/v1/decision/work-orders'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => WorkOrderModel.fromJson(e)).toList();
    }
    throw Exception('Failed to fetch work orders');
  }
}
