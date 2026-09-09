class TelemetryReading {
  final String timestamp;
  final double strainMicrostrain;
  final double vibrationMs2;
  final double crackPropagationMm;
  final double deflectionMm;
  final double tiltDeg;
  final double modalFrequencyHz;
  final double temperatureC;
  final double humidityPercent;

  TelemetryReading({
    required this.timestamp,
    required this.strainMicrostrain,
    required this.vibrationMs2,
    required this.crackPropagationMm,
    required this.deflectionMm,
    required this.tiltDeg,
    required this.modalFrequencyHz,
    required this.temperatureC,
    required this.humidityPercent,
  });

  factory TelemetryReading.fromJson(Map<String, dynamic> json) {
    return TelemetryReading(
      timestamp: json['timestamp'] ?? '',
      strainMicrostrain: (json['strain_microstrain'] as num?)?.toDouble() ?? 0.0,
      vibrationMs2: (json['vibration_ms2'] as num?)?.toDouble() ?? 0.0,
      crackPropagationMm: (json['crack_propagation_mm'] as num?)?.toDouble() ?? 0.0,
      deflectionMm: (json['deflection_mm'] as num?)?.toDouble() ?? 0.0,
      tiltDeg: (json['tilt_deg'] as num?)?.toDouble() ?? 0.0,
      modalFrequencyHz: (json['modal_frequency_hz'] as num?)?.toDouble() ?? 0.0,
      temperatureC: (json['temperature_c'] as num?)?.toDouble() ?? 0.0,
      humidityPercent: (json['humidity_percent'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp,
    'strain_microstrain': strainMicrostrain,
    'vibration_ms2': vibrationMs2,
    'crack_propagation_mm': crackPropagationMm,
    'deflection_mm': deflectionMm,
    'tilt_deg': tiltDeg,
    'modal_frequency_hz': modalFrequencyHz,
    'temperature_c': temperatureC,
    'humidity_percent': humidityPercent,
  };
}

class ConditionStateData {
  final int classIndex;
  final String conditionName;
  final double confidencePct;
  final String confidenceInterval95;
  final List<double> probabilities;
  final bool anomalyDetected;

  ConditionStateData({
    required this.classIndex,
    required this.conditionName,
    required this.confidencePct,
    required this.confidenceInterval95,
    required this.probabilities,
    required this.anomalyDetected,
  });

  factory ConditionStateData.fromJson(Map<String, dynamic> json) {
    return ConditionStateData(
      classIndex: json['class_index'] ?? 0,
      conditionName: json['condition_name'] ?? 'Normal / Healthy',
      confidencePct: (json['confidence_pct'] as num?)?.toDouble() ?? 0.0,
      confidenceInterval95: json['confidence_interval_95'] ?? '',
      probabilities: (json['probabilities'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [],
      anomalyDetected: json['anomaly_detected'] ?? false,
    );
  }
}

class TelemetryPacket {
  final String assetId;
  final int sequence;
  final TelemetryReading telemetry;
  final ConditionStateData conditionState;
  final double isolatedMechanicalStrain;
  final double thermalStrainOffset;

  TelemetryPacket({
    required this.assetId,
    required this.sequence,
    required this.telemetry,
    required this.conditionState,
    required this.isolatedMechanicalStrain,
    required this.thermalStrainOffset,
  });

  factory TelemetryPacket.fromJson(Map<String, dynamic> json) {
    return TelemetryPacket(
      assetId: json['asset_id'] ?? '',
      sequence: json['sequence'] ?? 0,
      telemetry: TelemetryReading.fromJson(json['telemetry'] ?? {}),
      conditionState: ConditionStateData.fromJson(json['condition_state'] ?? {}),
      isolatedMechanicalStrain:
          (json['isolated_mechanical_strain'] as num?)?.toDouble() ?? 0.0,
      thermalStrainOffset:
          (json['thermal_strain_offset'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
