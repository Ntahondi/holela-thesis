import 'dart:async';
import 'package:flutter/material.dart';
import '../../../../data/models/asset_model.dart';
import '../../../../data/models/telemetry_model.dart';
import '../../../../data/services/api_service.dart';
import '../../../../data/services/websocket_service.dart';
import '../../../core/theme.dart';
import '../../../core/widgets/condition_badge.dart';
import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/technical_chart.dart';

class DashboardView extends StatefulWidget {
  final CivilAssetModel currentAsset;
  final Function(int) onNavigateTab;

  const DashboardView({
    super.key,
    required this.currentAsset,
    required this.onNavigateTab,
  });

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  final WebSocketService _wsService = WebSocketService();
  StreamSubscription<TelemetryPacket>? _streamSub;

  final List<EngineeringDataPoint> _strainHistory = [];
  final List<EngineeringDataPoint> _vibrationHistory = [];
  final List<EngineeringDataPoint> _crackHistory = [];

  TelemetryPacket? _latestPacket;
  bool _isConnecting = true;
  String _statusMessage = 'Connecting to IoT Gateway...';

  @override
  void initState() {
    super.initState();
    _initWebSocket();
  }

  @override
  void didUpdateWidget(covariant DashboardView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.currentAsset.assetId != widget.currentAsset.assetId) {
      _strainHistory.clear();
      _vibrationHistory.clear();
      _crackHistory.clear();
      _initWebSocket();
    }
  }

  void _initWebSocket() {
    _streamSub?.cancel();
    setState(() {
      _isConnecting = true;
      _statusMessage = 'Connecting to ${widget.currentAsset.name} IoT stream...';
    });

    _wsService.connect(widget.currentAsset.assetId);

    _streamSub = _wsService.packetStream.listen(
      (packet) {
        if (!mounted) return;
        setState(() {
          _isConnecting = false;
          _latestPacket = packet;

          final timeStr = packet.telemetry.timestamp.split('T').last;

          _strainHistory.add(EngineeringDataPoint(
            value: packet.isolatedMechanicalStrain,
            secondaryValue: packet.telemetry.temperatureC,
            timestamp: timeStr,
          ));
          if (_strainHistory.length > 30) _strainHistory.removeAt(0);

          _vibrationHistory.add(EngineeringDataPoint(
            value: packet.telemetry.vibrationMs2,
            timestamp: timeStr,
          ));
          if (_vibrationHistory.length > 30) _vibrationHistory.removeAt(0);

          _crackHistory.add(EngineeringDataPoint(
            value: packet.telemetry.crackPropagationMm,
            timestamp: timeStr,
          ));
          if (_crackHistory.length > 30) _crackHistory.removeAt(0);
        });
      },
      onError: (err) {
        if (!mounted) return;
        setState(() {
          _statusMessage = 'Stream connection error. Retrying...';
        });
      },
    );
  }

  @override
  void dispose() {
    _streamSub?.cancel();
    _wsService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final packet = _latestPacket;
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
              // Unified Civil Infrastructure Diagnostic & Status Header
              _buildAssetOverviewBanner(theme, packet),
              const SizedBox(height: 16),

              // Precision Instrumentation Telemetry Metric Grid
              _buildTelemetryMetricGrid(packet),
              const SizedBox(height: 16),

              // Engineering Technical Charts (Dual Canvas)
              LayoutBuilder(
                builder: (context, constraints) {
                  final isWide = constraints.maxWidth > 920;
                  if (isWide) {
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          flex: 6,
                          child: TechnicalEngineeringChart(
                            title:
                                'MECHANICAL STRAIN vs THERMAL DRIFT (ε_mech = ε_tot - αΔT)',
                            primaryUnit: 'Isolated Strain (με)',
                            secondaryUnit: 'Drift Offset (με)',
                            dataPoints: _strainHistory,
                            criticalThreshold: 950.0,
                            primaryColor: CivilColors.seriesPrimary,
                            secondaryColor: CivilColors.seriesSecondary,
                            height: 220,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          flex: 4,
                          child: TechnicalEngineeringChart(
                            title: 'TRI-AXIAL MODAL ACCELERATION DYNAMICS',
                            primaryUnit: 'Acceleration (m/s²)',
                            dataPoints: _vibrationHistory,
                            criticalThreshold: 2.2,
                            primaryColor: CivilColors.seriesPrimary,
                            height: 220,
                          ),
                        ),
                      ],
                    );
                  } else {
                    return Column(
                      children: [
                        TechnicalEngineeringChart(
                          title:
                              'MECHANICAL STRAIN (ε_mech = ε_tot - αΔT)',
                          primaryUnit: 'Strain (με)',
                          dataPoints: _strainHistory,
                          criticalThreshold: 950.0,
                          primaryColor: CivilColors.seriesPrimary,
                          height: 200,
                        ),
                        const SizedBox(height: 16),
                        TechnicalEngineeringChart(
                          title: 'TRI-AXIAL MODAL ACCELERATION',
                          primaryUnit: 'Acceleration (m/s²)',
                          dataPoints: _vibrationHistory,
                          criticalThreshold: 2.2,
                          primaryColor: CivilColors.seriesPrimary,
                          height: 200,
                        ),
                      ],
                    );
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAssetOverviewBanner(ThemeData theme, TelemetryPacket? packet) {
    final asset = widget.currentAsset;
    final condIndex = packet?.conditionState.classIndex ?? 0;
    final condName = packet?.conditionState.conditionName ?? asset.conditionState;
    final confPct = packet?.conditionState.confidencePct;
    final uncertainty = packet?.conditionState.confidenceInterval95;
    final hasAnomaly = packet?.conditionState.anomalyDetected ?? false;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? CivilColors.darkSurface : CivilColors.lightSurface,
        border: Border.all(color: theme.colorScheme.outline),
        borderRadius: BorderRadius.circular(4),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row: Identity & Status Badge (Wrap to ensure zero overflow on any width)
          LayoutBuilder(
            builder: (context, constraints) {
              final isCompact = constraints.maxWidth < 680;

              final identityBlock = Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 8,
                    runSpacing: 4,
                    children: [
                      Text(
                        asset.name.toUpperCase(),
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.3,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: isDark ? CivilColors.darkBorder : CivilColors.lightBorder,
                          borderRadius: BorderRadius.circular(3),
                        ),
                        child: Text(
                          asset.assetId,
                          style: TextStyle(
                            fontSize: 10,
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.w600,
                            color: isDark ? CivilColors.darkTextSecondary : CivilColors.lightTextSecondary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${asset.structureType} • Built ${asset.yearConstructed} • ${asset.locationRegion}, Tanzania (${asset.roadClass} Corridor)',
                    style: theme.textTheme.bodyMedium?.copyWith(fontSize: 11),
                  ),
                ],
              );

              final badgeBlock = ConditionBadge(
                conditionIndex: condIndex,
                conditionName: condName,
                confidencePct: confPct,
                uncertaintyStr: uncertainty,
                compact: isCompact,
              );

              if (isCompact) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    identityBlock,
                    const SizedBox(height: 10),
                    badgeBlock,
                  ],
                );
              }

              return Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: identityBlock),
                  const SizedBox(width: 16),
                  badgeBlock,
                ],
              );
            },
          ),

          const Divider(height: 24),

          // Engineering Diagnostic Strip (Physical Decoupling, MC-Dropout, Action)
          Wrap(
            spacing: 12,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            alignment: WrapAlignment.spaceBetween,
            children: [
              Wrap(
                spacing: 8,
                runSpacing: 6,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  _DiagnosticChip(
                    label: 'PHYSICS DECOUPLING',
                    value: 'Offset ΔT=${packet?.thermalStrainOffset.toStringAsFixed(1) ?? "12.4"} με (α=11.5 με/°C)',
                    isDark: isDark,
                  ),
                  _DiagnosticChip(
                    label: 'INFERENCE MODEL',
                    value: '1D-CNN (30 MC-Dropout Passes)',
                    isDark: isDark,
                  ),
                  _DiagnosticChip(
                    label: 'STATUS',
                    value: hasAnomaly ? 'Anomaly Detected' : 'Nominal Integrity',
                    isAlert: hasAnomaly,
                    isDark: isDark,
                  ),
                ],
              ),
              OutlinedButton.icon(
                onPressed: () => widget.onNavigateTab(2),
                icon: const Icon(Icons.assignment_outlined, size: 14),
                label: const Text('DISPATCH IDSS'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(3)),
                  side: BorderSide(color: theme.colorScheme.outline),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTelemetryMetricGrid(TelemetryPacket? packet) {
    final t = packet?.telemetry;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 950;
        final count = isWide ? 4 : (constraints.maxWidth > 550 ? 2 : 1);

        final cards = [
          TechnicalMetricCard(
            label: 'Mechanical Strain',
            channelId: 'CH-01 [FBG FLANGE]',
            value: packet != null
                ? packet.isolatedMechanicalStrain.toStringAsFixed(1)
                : '782.4',
            unit: 'με',
            subtext: 'Limit: 950.0 με (Isolated)',
            isAlert: (packet?.isolatedMechanicalStrain ?? 0) > 950,
          ),
          TechnicalMetricCard(
            label: 'Modal Vibration',
            channelId: 'CH-02 [MEMS ACCEL]',
            value: t != null ? t.vibrationMs2.toStringAsFixed(2) : '1.24',
            unit: 'm/s²',
            subtext: 'Service Limit: 2.20 m/s²',
            isAlert: (t?.vibrationMs2 ?? 0) > 2.2,
          ),
          TechnicalMetricCard(
            label: 'Crack Opening Width',
            channelId: 'CH-03 [LVDT JOINT]',
            value: t != null ? t.crackPropagationMm.toStringAsFixed(3) : '0.015',
            unit: 'mm',
            subtext: 'Eurocode 2 Limit: 0.20 mm',
            isAlert: (t?.crackPropagationMm ?? 0) > 0.20,
          ),
          TechnicalMetricCard(
            label: 'Modal Frequency',
            channelId: 'CH-04 [DYNAMIC FFT]',
            value: t != null ? t.modalFrequencyHz.toStringAsFixed(2) : '1.88',
            unit: 'Hz',
            subtext: 'Baseline Flexural: 1.88 Hz',
          ),
        ];

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: cards.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: count,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            mainAxisExtent: 96,
          ),
          itemBuilder: (context, idx) => cards[idx],
        );
      },
    );
  }
}

class _DiagnosticChip extends StatelessWidget {
  final String label;
  final String value;
  final bool isAlert;
  final bool isDark;

  const _DiagnosticChip({
    required this.label,
    required this.value,
    this.isAlert = false,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: isAlert
            ? CivilColors.critical.withOpacity(0.1)
            : (isDark ? CivilColors.darkBorder.withOpacity(0.5) : CivilColors.lightBorder.withOpacity(0.6)),
        border: Border.all(
          color: isAlert ? CivilColors.critical : (isDark ? CivilColors.darkBorder : CivilColors.lightBorder),
        ),
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text.rich(
        TextSpan(
          children: [
            TextSpan(
              text: '$label: ',
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: isAlert ? CivilColors.critical : (isDark ? CivilColors.darkTextMuted : CivilColors.lightTextMuted),
                letterSpacing: 0.4,
              ),
            ),
            TextSpan(
              text: value,
              style: TextStyle(
                fontSize: 10,
                fontFamily: 'monospace',
                fontWeight: FontWeight.w600,
                color: isAlert ? CivilColors.critical : (isDark ? CivilColors.darkTextPrimary : CivilColors.lightTextPrimary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
