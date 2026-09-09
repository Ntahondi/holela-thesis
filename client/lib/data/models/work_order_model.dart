class WorkOrderModel {
  final String orderId;
  final String assetId;
  final String conditionEvaluated;
  final double priorityIndexScore;
  final String urgencyLevel;
  final String recommendedAction;
  final String assignedAgency;
  final String estimatedBudgetTier;
  final String timestampCreated;
  final String status;

  WorkOrderModel({
    required this.orderId,
    required this.assetId,
    required this.conditionEvaluated,
    required this.priorityIndexScore,
    required this.urgencyLevel,
    required this.recommendedAction,
    required this.assignedAgency,
    required this.estimatedBudgetTier,
    required this.timestampCreated,
    required this.status,
  });

  factory WorkOrderModel.fromJson(Map<String, dynamic> json) {
    return WorkOrderModel(
      orderId: json['order_id'] ?? '',
      assetId: json['asset_id'] ?? '',
      conditionEvaluated: json['condition_evaluated'] ?? '',
      priorityIndexScore: (json['priority_index_score'] as num?)?.toDouble() ?? 0.0,
      urgencyLevel: json['urgency_level'] ?? 'Routine',
      recommendedAction: json['recommended_action'] ?? '',
      assignedAgency: json['assigned_agency'] ?? 'TANROADS Head Office',
      estimatedBudgetTier: json['estimated_budget_tier'] ?? 'Tier 1 (< 5M TZS)',
      timestampCreated: json['timestamp_created'] ?? '',
      status: json['status'] ?? 'Pending Approval',
    );
  }
}
