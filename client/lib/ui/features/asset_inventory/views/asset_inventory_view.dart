import 'package:flutter/material.dart';
import '../../../../data/models/asset_model.dart';
import '../../../../data/services/api_service.dart';
import '../../../core/theme.dart';

class AssetInventoryView extends StatefulWidget {
  final List<CivilAssetModel> assets;
  final CivilAssetModel selectedAsset;
  final Function(CivilAssetModel) onSelectAsset;
  final Function(int) onNavigateTab;

  const AssetInventoryView({
    super.key,
    required this.assets,
    required this.selectedAsset,
    required this.onSelectAsset,
    required this.onNavigateTab,
  });

  @override
  State<AssetInventoryView> createState() => _AssetInventoryViewState();
}

class _AssetInventoryViewState extends State<AssetInventoryView> {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _selectedInstrumentation;
  bool _isLoadingInstrumentation = false;
  String? _insError;

  @override
  void initState() {
    super.initState();
    _loadInstrumentation(widget.selectedAsset.assetId);
  }

  Future<void> _loadInstrumentation(String assetId) async {
    setState(() {
      _isLoadingInstrumentation = true;
      _insError = null;
    });

    try {
      final res = await _apiService.getAssetInstrumentation(assetId);
      setState(() {
        _selectedInstrumentation = res;
        _isLoadingInstrumentation = false;
      });
    } catch (e) {
      setState(() {
        _insError = 'Could not load sensor specs: $e';
        _isLoadingInstrumentation = false;
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
          // Banner
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: theme.cardColor,
              border: Border.all(color: theme.colorScheme.outline),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                const Icon(Icons.account_balance_outlined,
                    color: CivilColors.steelBlue, size: 28),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'NATIONAL CIVIL CONCRETE INFRASTRUCTURE REGISTRY',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Multi-structure concrete assets: Bridges, Hydroelectric Dams, Commercial Buildings, and Port Wharves (TANROADS, TANESCO, TPA, TBA, TRC). '
                        'Section 5.6.4 Physical Sensor Instrumentation Architecture.',
                        style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Assets Grid & Instrumentation Details
          LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth > 850;

              final listPanel = Column(
                children: [
                  for (final asset in widget.assets) ...[
                    _buildAssetCard(theme, asset),
                    const SizedBox(height: 10),
                  ]
                ],
              );

              final instrumentationPanel = Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.cardColor,
                  border: Border.all(color: theme.colorScheme.outline),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: _buildInstrumentationDetails(theme),
              );

              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 5, child: listPanel),
                    const SizedBox(width: 16),
                    Expanded(flex: 5, child: instrumentationPanel),
                  ],
                );
              } else {
                return Column(
                  children: [
                    listPanel,
                    const SizedBox(height: 16),
                    instrumentationPanel,
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

  Widget _buildAssetCard(ThemeData theme, CivilAssetModel asset) {
    final isSelected = asset.assetId == widget.selectedAsset.assetId;
    final healthPct = (asset.currentHealthIndex * 100).toStringAsFixed(0);

    return InkWell(
      onTap: () {
        widget.onSelectAsset(asset);
        _loadInstrumentation(asset.assetId);
      },
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected
              ? CivilColors.steelBlue.withOpacity(0.08)
              : theme.cardColor,
          border: Border.all(
            color: isSelected
                ? CivilColors.steelBlue
                : theme.colorScheme.outline,
            width: isSelected ? 1.5 : 1.0,
          ),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    asset.name,
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 14,
                      color: isSelected
                          ? CivilColors.steelBlue
                          : theme.colorScheme.onSurface,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: CivilColors.healthy.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(3),
                  ),
                  child: Text(
                    'Health Index: $healthPct%',
                    style: const TextStyle(
                      color: CivilColors.healthy,
                      fontWeight: FontWeight.w700,
                      fontSize: 11,
                      fontFamily: 'monospace',
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${asset.structureType} • Built ${asset.yearConstructed}',
              style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    '${asset.locationRegion} • ${asset.roadClass} (GPS: ${asset.gpsLatitude.toStringAsFixed(3)}, ${asset.gpsLongitude.toStringAsFixed(3)})',
                    style: theme.textTheme.bodySmall?.copyWith(fontSize: 10),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (isSelected) ...[
                  const SizedBox(width: 8),
                  const Text(
                    'ACTIVE MONITORING',
                    style: TextStyle(
                      color: CivilColors.steelBlue,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ]
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInstrumentationDetails(ThemeData theme) {
    if (_isLoadingInstrumentation) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(40),
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }

    final data = _selectedInstrumentation;
    if (data == null) {
      return Center(
        child: Text('Select an asset to view sensor specifications.',
            style: theme.textTheme.bodySmall),
      );
    }

    final sensors = (data['sensors_installed'] as List<dynamic>?) ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 8,
          runSpacing: 8,
          children: [
            Text('SENSOR INSTRUMENTATION MATRIX',
                style: theme.textTheme.titleSmall),
            ElevatedButton(
              onPressed: () => widget.onNavigateTab(0), // Jump to live dashboard
              style: ElevatedButton.styleFrom(
                backgroundColor: CivilColors.steelBlue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
              ),
              child: const Text('OPEN LIVE STREAM', style: TextStyle(fontSize: 11)),
            )
          ],
        ),
        const SizedBox(height: 4),
        Text(
          'Target: ${data['asset_name']} (${data['structure_type']})',
          style: theme.textTheme.bodySmall?.copyWith(fontSize: 11),
        ),
        const Divider(height: 16),
        for (final s in sensors) ...[
          Container(
            padding: const EdgeInsets.all(10),
            margin: const EdgeInsets.only(bottom: 8),
            decoration: BoxDecoration(
              color: theme.colorScheme.outline.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: theme.colorScheme.outline),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        s['type'] ?? '',
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      s['parameter'] ?? '',
                      style: const TextStyle(
                        fontSize: 11,
                        color: CivilColors.steelBlue,
                        fontWeight: FontWeight.w600,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text('Location: ${s['location'] ?? ''}',
                    style: theme.textTheme.bodySmall?.copyWith(fontSize: 11)),
                Text(
                  'Sampling: ${s['sampling_frequency'] ?? ''} • Range: ${s['nominal_range'] ?? ''}',
                  style: theme.textTheme.bodySmall?.copyWith(fontSize: 10),
                ),
                if (s['critical_threshold'] != null)
                  Text(
                    'Critical Alert: ${s['critical_threshold']}',
                    style: const TextStyle(
                      color: CivilColors.critical,
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      fontFamily: 'monospace',
                    ),
                  ),
              ],
            ),
          )
        ],
        const SizedBox(height: 8),
        Text(
          'Edge Gateway: ${data['edge_gateway'] ?? 'ARM Cortex Gateway'}',
          style: theme.textTheme.bodySmall?.copyWith(fontSize: 10, fontStyle: FontStyle.italic),
        )
      ],
    );
  }
}
