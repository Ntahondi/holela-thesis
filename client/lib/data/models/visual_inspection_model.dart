class VisualInspectionResult {
  final int defectClassIndex;
  final String defectName;
  final double confidencePct;
  final List<double> probabilities;
  final String severityLevel;
  final double estimatedSurfaceDefectRatioPct;
  final String gradcamHeatmapBase64;
  final bool isOutOfDistribution;
  final String? oodWarning;

  VisualInspectionResult({
    required this.defectClassIndex,
    required this.defectName,
    required this.confidencePct,
    required this.probabilities,
    required this.severityLevel,
    required this.estimatedSurfaceDefectRatioPct,
    required this.gradcamHeatmapBase64,
    this.isOutOfDistribution = false,
    this.oodWarning,
  });

  factory VisualInspectionResult.fromJson(Map<String, dynamic> json) {
    return VisualInspectionResult(
      defectClassIndex: json['defect_class_index'] ?? 0,
      defectName: json['defect_name'] ?? 'Unknown Defect',
      confidencePct: (json['confidence_pct'] as num?)?.toDouble() ?? 0.0,
      probabilities: (json['probabilities'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [],
      severityLevel: json['severity_level'] ?? 'Normal',
      estimatedSurfaceDefectRatioPct:
          (json['estimated_surface_defect_ratio_pct'] as num?)?.toDouble() ?? 0.0,
      gradcamHeatmapBase64: json['gradcam_heatmap_base64'] ?? '',
      isOutOfDistribution: json['is_out_of_distribution'] ?? false,
      oodWarning: json['ood_warning'],
    );
  }
}
