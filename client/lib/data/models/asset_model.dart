class CivilAssetModel {
  final String assetId;
  final String name;
  final String structureType;
  final String locationRegion;
  final double gpsLatitude;
  final double gpsLongitude;
  final String roadClass;
  final int yearConstructed;
  final double currentHealthIndex;
  final String conditionState;
  final double importanceFactor;

  CivilAssetModel({
    required this.assetId,
    required this.name,
    required this.structureType,
    required this.locationRegion,
    required this.gpsLatitude,
    required this.gpsLongitude,
    required this.roadClass,
    required this.yearConstructed,
    required this.currentHealthIndex,
    required this.conditionState,
    required this.importanceFactor,
  });

  factory CivilAssetModel.fromJson(Map<String, dynamic> json) {
    return CivilAssetModel(
      assetId: json['asset_id'] ?? '',
      name: json['name'] ?? '',
      structureType: json['structure_type'] ?? '',
      locationRegion: json['location_region'] ?? '',
      gpsLatitude: (json['gps_latitude'] as num?)?.toDouble() ?? 0.0,
      gpsLongitude: (json['gps_longitude'] as num?)?.toDouble() ?? 0.0,
      roadClass: json['road_class'] ?? 'Trunk',
      yearConstructed: json['year_constructed'] ?? 2020,
      currentHealthIndex: (json['current_health_index'] as num?)?.toDouble() ?? 1.0,
      conditionState: json['condition_state'] ?? 'Normal / Healthy',
      importanceFactor: (json['importance_factor'] as num?)?.toDouble() ?? 1.0,
    );
  }
}
