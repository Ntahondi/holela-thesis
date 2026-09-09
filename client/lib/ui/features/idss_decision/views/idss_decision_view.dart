import 'package:flutter/material.dart';
import '../../../../data/models/asset_model.dart';
import '../../../../data/models/work_order_model.dart';
import '../../../../data/services/api_service.dart';
import '../../../core/theme.dart';

class IdssDecisionView extends StatefulWidget {
  final CivilAssetModel currentAsset;

  const IdssDecisionView({super.key, required this.currentAsset});

  @override
  State<IdssDecisionView> createState() => _IdssDecisionViewState();
}

class _IdssDecisionViewState extends State<IdssDecisionView> {
  final ApiService _apiService = ApiService();

  int _selectedConditionClass = 1; // Default: Minor Deterioration
  String _selectedRoadClass = 'Trunk';
  double _importanceWeight = 1.4;

  final double _maxStrain = 780.0;
  final double _maxVibration = 1.35;
  final double _crackWidthMm = 0.02;

  WorkOrderModel? _latestEvaluatedOrder;
  List<WorkOrderModel> _workOrders = [];
  bool _isEvaluating = false;
  bool _isLoadingOrders = false;
  String? _statusMessage;

  @override
  void initState() {
    super.initState();
    _selectedRoadClass = widget.currentAsset.roadClass;
    _importanceWeight = widget.currentAsset.importanceFactor;
    _loadWorkOrders();
  }

  Future<void> _loadWorkOrders() async {
    setState(() => _isLoadingOrders = true);
    try {
      final list = await _apiService.getWorkOrders();
      setState(() {
        _workOrders = list;
        _isLoadingOrders = false;
      });
    } catch (e) {
      setState(() => _isLoadingOrders = false);
    }
  }

  Future<void> _runIdssEvaluation() async {
    setState(() {
      _isEvaluating = true;
      _statusMessage = null;
    });

    // Construct class probabilities based on selected class
    final probs = [0.05, 0.05, 0.05, 0.05];
    probs[_selectedConditionClass] = 0.85;

    try {
      final order = await _apiService.evaluateDecision(
        assetId: widget.currentAsset.assetId,
        predictedClass: _selectedConditionClass,
        classProbabilities: probs,
        maxStrain: _maxStrain,
        maxVibration: _maxVibration,
        crackPropagationMm: _crackWidthMm,
        roadClass: _selectedRoadClass,
        importanceWeight: _importanceWeight,
      );

      setState(() {
        _latestEvaluatedOrder = order;
        _isEvaluating = false;
        _statusMessage = 'Work Order ${order.orderId} generated & dispatched to ${order.assignedAgency}';
      });
      _loadWorkOrders();
    } catch (e) {
      setState(() {
        _isEvaluating = false;
        _statusMessage = 'Evaluation failed: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < 700;

    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 1380),
        child: SingleChildScrollView(
          padding: EdgeInsets.all(isMobile ? 12 : 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
          // Banner Description
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: theme.cardColor,
              border: Border.all(color: theme.colorScheme.outline),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                const Icon(Icons.rule_folder_outlined,
                    color: CivilColors.steelBlue, size: 28),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'INTELLIGENT DECISION SUPPORT SYSTEM (IDSS) • CHAPTER 6',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Calculates Maintenance Priority Index (MPI = f(Deterioration, Road Class, Traffic Criticality, Budget Limits)). '
                        'Automates work order generation for TANROADS & TRC regional engineers.',
                        style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Evaluation Input Controls & Live Calculation
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 850;

              final inputPanel = Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.cardColor,
                  border: Border.all(color: theme.colorScheme.outline),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('PARAMETRIC DECISION CRITERIA',
                        style: theme.textTheme.titleSmall),
                    const Divider(height: 20),
                    
                    // Condition state selector
                    Text('Inferred Structural Condition State:',
                        style: theme.textTheme.labelMedium),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<int>(
                      value: _selectedConditionClass,
                      decoration: const InputDecoration(
                        isDense: true,
                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem(value: 0, child: Text('Normal / Healthy (State 0)')),
                        DropdownMenuItem(value: 1, child: Text('Minor Deterioration (State 1)')),
                        DropdownMenuItem(value: 2, child: Text('Moderate Distress (State 2)')),
                        DropdownMenuItem(value: 3, child: Text('Critical Damage (State 3)')),
                      ],
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedConditionClass = val);
                      },
                    ),
                    const SizedBox(height: 14),

                    // Civil Asset Classification
                    Text('Civil Asset / Infrastructure Classification:',
                        style: theme.textTheme.labelMedium),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      value: const [
                        'Trunk',
                        'Hydro Dam',
                        'Marine Port',
                        'Heavy Rail',
                        'Building',
                        'Institutional',
                      ].contains(_selectedRoadClass)
                          ? _selectedRoadClass
                          : 'Trunk',
                      isExpanded: true,
                      decoration: const InputDecoration(
                        isDense: true,
                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'Trunk', child: Text('Trunk Highway Bridge (TANROADS - 1.4x)', overflow: TextOverflow.ellipsis)),
                        DropdownMenuItem(value: 'Hydro Dam', child: Text('Hydro Dam Spillway (TANESCO - 1.8x)', overflow: TextOverflow.ellipsis)),
                        DropdownMenuItem(value: 'Marine Port', child: Text('Marine Quay Wall / Wharf (TPA - 1.5x)', overflow: TextOverflow.ellipsis)),
                        DropdownMenuItem(value: 'Heavy Rail', child: Text('Heavy Rail Viaduct (TRC SGR - 1.6x)', overflow: TextOverflow.ellipsis)),
                        DropdownMenuItem(value: 'Building', child: Text('Commercial / Public Building (TBA - 1.2x)', overflow: TextOverflow.ellipsis)),
                        DropdownMenuItem(value: 'Institutional', child: Text('Institutional Frame (UDSM - 1.0x)', overflow: TextOverflow.ellipsis)),
                      ],
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedRoadClass = val);
                      },
                    ),
                    const SizedBox(height: 14),

                    // Importance Factor Slider
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Criticality Factor (w_imp):', style: theme.textTheme.labelMedium),
                        Text(_importanceWeight.toStringAsFixed(2),
                            style: const TextStyle(fontWeight: FontWeight.w700, fontFamily: 'monospace')),
                      ],
                    ),
                    Slider(
                      value: _importanceWeight,
                      min: 1.0,
                      max: 2.0,
                      divisions: 10,
                      label: _importanceWeight.toStringAsFixed(2),
                      activeColor: CivilColors.steelBlue,
                      onChanged: (val) => setState(() => _importanceWeight = val),
                    ),
                    const SizedBox(height: 10),

                    // Dispatch Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isEvaluating ? null : _runIdssEvaluation,
                        icon: _isEvaluating
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Icon(Icons.send_outlined, size: 16),
                        label: Text(_isEvaluating
                            ? 'EVALUATING MULTI-CRITERIA...'
                            : 'EVALUATE & DISPATCH WORK ORDER'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: CivilColors.steelBlue,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                        ),
                      ),
                    ),
                  ],
                ),
              );

              final orderPanel = Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.cardColor,
                  border: Border.all(color: theme.colorScheme.outline),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: _latestEvaluatedOrder != null
                    ? _buildEvaluatedOrderCard(theme, _latestEvaluatedOrder!)
                    : Center(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 40),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.pending_actions, size: 36, color: CivilColors.gridLine),
                              const SizedBox(height: 8),
                              Text('No evaluation executed for current session.',
                                  style: theme.textTheme.bodySmall),
                              const SizedBox(height: 4),
                              Text('Click "Evaluate & Dispatch" to generate MPI.',
                                  style: theme.textTheme.bodySmall?.copyWith(fontSize: 10)),
                            ],
                          ),
                        ),
                      ),
              );

              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 5, child: inputPanel),
                    const SizedBox(width: 16),
                    Expanded(flex: 5, child: orderPanel),
                  ],
                );
              } else {
                return Column(
                  children: [
                    inputPanel,
                    const SizedBox(height: 16),
                    orderPanel,
                  ],
                );
              }
            },
          ),
          const SizedBox(height: 24),

          // Active Work Orders Table
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  'DISPATCHED MAINTENANCE WORK ORDERS REGISTRY',
                  style: theme.textTheme.titleSmall,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.refresh, size: 18),
                onPressed: _loadWorkOrders,
                tooltip: 'Refresh Orders',
              ),
            ],
          ),
          const SizedBox(height: 8),
          _buildWorkOrdersTable(theme),
        ],
      ),
    ),
  ),
);
  }

  Widget _buildEvaluatedOrderCard(ThemeData theme, WorkOrderModel order) {
    final mpi = order.priorityIndexScore;
    Color mpiColor = CivilColors.healthy;
    if (mpi > 75) {
      mpiColor = CivilColors.critical;
    } else if (mpi > 50) {
      mpiColor = CivilColors.moderate;
    } else if (mpi > 25) {
      mpiColor = CivilColors.minor;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('IDSS EVALUATION RESULT', style: theme.textTheme.titleSmall),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: mpiColor.withOpacity(0.15),
                border: Border.all(color: mpiColor),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'MPI: ${mpi.toStringAsFixed(1)} / 100',
                style: TextStyle(
                  color: mpiColor,
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
            )
          ],
        ),
        const Divider(height: 20),
        _buildInfoRow('Work Order Number:', order.orderId),
        _buildInfoRow('Target Infrastructure:', order.assetId),
        _buildInfoRow('Assigned Agency:', order.assignedAgency),
        _buildInfoRow('Urgency Tier:', order.urgencyLevel),
        _buildInfoRow('Estimated Budget Tier:', order.estimatedBudgetTier),
        _buildInfoRow('Dispatched Status:', order.status),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: theme.colorScheme.outline.withOpacity(0.1),
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: theme.colorScheme.outline),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('RECOMMENDED INTERVENTION ACTION:',
                  style: theme.textTheme.labelMedium?.copyWith(fontSize: 10, fontWeight: FontWeight.w700)),
              const SizedBox(height: 4),
              Text(order.recommendedAction,
                  style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              value,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.end,
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWorkOrdersTable(ThemeData theme) {
    if (_isLoadingOrders) {
      return const Center(
          child: Padding(
        padding: EdgeInsets.all(20),
        child: CircularProgressIndicator(strokeWidth: 2),
      ));
    }

    if (_workOrders.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: theme.cardColor,
          border: Border.all(color: theme.colorScheme.outline),
          borderRadius: BorderRadius.circular(6),
        ),
        alignment: Alignment.center,
        child: Text('No active work orders registered yet.',
            style: theme.textTheme.bodySmall),
      );
    }

    return Container(
      decoration: BoxDecoration(
        color: theme.cardColor,
        border: Border.all(color: theme.colorScheme.outline),
        borderRadius: BorderRadius.circular(6),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: _workOrders.length,
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (context, idx) {
          final wo = _workOrders[idx];
          final score = wo.priorityIndexScore;
          Color badgeCol = CivilColors.healthy;
          if (score > 75) {
            badgeCol = CivilColors.critical;
          } else if (score > 50) {
            badgeCol = CivilColors.moderate;
          } else if (score > 25) {
            badgeCol = CivilColors.minor;
          }

          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                  decoration: BoxDecoration(
                    color: badgeCol.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    score.toStringAsFixed(0),
                    style: TextStyle(
                      color: badgeCol,
                      fontWeight: FontWeight.w700,
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              wo.orderId,
                              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Flexible(
                            child: Text(
                              '• ${wo.assetId}',
                              style: theme.textTheme.bodySmall,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${wo.urgencyLevel} • ${wo.assignedAgency} • ${wo.estimatedBudgetTier}',
                        style: theme.textTheme.bodySmall?.copyWith(fontSize: 11),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.outline.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: Text(
                    wo.status,
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
