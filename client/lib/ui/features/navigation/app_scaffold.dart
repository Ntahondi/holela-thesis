import 'package:flutter/material.dart';
import '../../../data/models/asset_model.dart';
import '../../../data/services/api_service.dart';
import '../../core/theme.dart';
import '../../core/theme_notifier.dart';
import '../dashboard/views/dashboard_view.dart';
import '../visual_inspection/views/visual_inspection_view.dart';
import '../idss_decision/views/idss_decision_view.dart';
import '../asset_inventory/views/asset_inventory_view.dart';

class AppScaffold extends StatefulWidget {
  final ThemeNotifier themeNotifier;

  const AppScaffold({super.key, required this.themeNotifier});

  @override
  State<AppScaffold> createState() => _AppScaffoldState();
}

class _AppScaffoldState extends State<AppScaffold> {
  final ApiService _apiService = ApiService();
  int _currentTabIndex = 0;

  List<CivilAssetModel> _assets = [];
  CivilAssetModel? _selectedAsset;
  bool _isLoadingAssets = true;
  String? _loadError;

  @override
  void initState() {
    super.initState();
    _fetchAssets();
  }

  Future<void> _fetchAssets() async {
    setState(() {
      _isLoadingAssets = true;
      _loadError = null;
    });

    try {
      final list = await _apiService.getAssets();
      setState(() {
        _assets = list;
        if (list.isNotEmpty) {
          _selectedAsset = list[0]; // Default: Tanzanite Bridge
        }
        _isLoadingAssets = false;
      });
    } catch (e) {
      setState(() {
        _loadError = 'Failed to connect to backend: $e';
        _isLoadingAssets = false;
        // Fallback default asset for offline operation
        _selectedAsset = CivilAssetModel(
          assetId: 'TZ-TANROADS-BR-004',
          name: 'Tanzanite Bridge',
          structureType: 'Extradosed Cable-Stayed Concrete Bridge',
          locationRegion: 'Dar es Salaam',
          gpsLatitude: -6.8041,
          gpsLongitude: 39.2906,
          roadClass: 'Trunk',
          yearConstructed: 2022,
          currentHealthIndex: 0.82,
          conditionState: 'Minor Deterioration',
          importanceFactor: 1.5,
        );
        _assets = [_selectedAsset!];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_isLoadingAssets) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(strokeWidth: 2),
              const SizedBox(height: 16),
              Text(
                'SMMS TANZANIA • INITIALIZING INFRASTRUCTURE REGISTRY...',
                style: theme.textTheme.bodySmall?.copyWith(letterSpacing: 0.5),
              ),
            ],
          ),
        ),
      );
    }

    final currentAsset = _selectedAsset ?? _assets.first;
    final screenWidth = MediaQuery.of(context).size.width;
    final isMobile = screenWidth < 640;

    final destinations = const [
      NavigationDestination(
        icon: Icon(Icons.dashboard_outlined),
        selectedIcon: Icon(Icons.dashboard),
        label: 'SHM Live',
      ),
      NavigationDestination(
        icon: Icon(Icons.photo_camera_outlined),
        selectedIcon: Icon(Icons.photo_camera),
        label: 'Visual XAI',
      ),
      NavigationDestination(
        icon: Icon(Icons.rule_folder_outlined),
        selectedIcon: Icon(Icons.rule_folder),
        label: 'IDSS',
      ),
      NavigationDestination(
        icon: Icon(Icons.account_balance_outlined),
        selectedIcon: Icon(Icons.account_balance),
        label: 'Registry',
      ),
    ];

    final mainContent = IndexedStack(
      index: _currentTabIndex,
      children: [
        DashboardView(
          currentAsset: currentAsset,
          onNavigateTab: (tab) => setState(() => _currentTabIndex = tab),
        ),
        const VisualInspectionView(),
        IdssDecisionView(currentAsset: currentAsset),
        AssetInventoryView(
          assets: _assets,
          selectedAsset: currentAsset,
          onSelectAsset: (a) => setState(() => _selectedAsset = a),
          onNavigateTab: (tab) => setState(() => _currentTabIndex = tab),
        ),
      ],
    );

    return Scaffold(
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(56),
        child: Container(
          decoration: BoxDecoration(
            color: theme.appBarTheme.backgroundColor,
            border: Border(
              bottom: BorderSide(color: theme.colorScheme.outline, width: 1),
            ),
          ),
          padding: EdgeInsets.symmetric(horizontal: isMobile ? 8 : 16),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final isCompact = constraints.maxWidth < 800;
              final isVeryCompact = constraints.maxWidth < 520;

              return Row(
                children: [
                  // Logo & System Title
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(5),
                        decoration: BoxDecoration(
                          color: CivilColors.primary,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Icon(Icons.apartment_outlined,
                            color: Colors.white, size: 16),
                      ),
                      const SizedBox(width: 8),
                      Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isVeryCompact ? 'SMMS' : 'TANROADS • SMMS',
                            style: const TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 12,
                              letterSpacing: 0.6,
                            ),
                          ),
                          if (!isCompact)
                            Text(
                              'SMART INFRASTRUCTURE MAINTENANCE MANAGEMENT',
                              style: theme.textTheme.bodySmall?.copyWith(
                                fontSize: 9,
                                letterSpacing: 0.3,
                              ),
                            ),
                        ],
                      ),
                    ],
                  ),
                  SizedBox(width: isVeryCompact ? 6 : 12),

                  // Active Asset Selector Dropdown (Constrained & Ellipsized)
                  if (_assets.isNotEmpty)
                    ConstrainedBox(
                      constraints: BoxConstraints(
                        maxWidth: isVeryCompact ? 115 : (isCompact ? 160 : 250),
                      ),
                      child: Container(
                        height: 30,
                        padding: const EdgeInsets.symmetric(horizontal: 6),
                        decoration: BoxDecoration(
                          color: theme.cardColor,
                          border: Border.all(color: theme.colorScheme.outline),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            isExpanded: true,
                            value: _assets.any((a) => a.assetId == currentAsset.assetId)
                                ? currentAsset.assetId
                                : (_assets.isNotEmpty ? _assets.first.assetId : null),
                            icon: const Icon(Icons.arrow_drop_down, size: 16),
                            style: theme.textTheme.bodyMedium?.copyWith(
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                            ),
                            items: _assets.map((a) {
                              return DropdownMenuItem<String>(
                                value: a.assetId,
                                child: Text(
                                  isVeryCompact ? a.name.split(' ').first : (isCompact ? a.name : '${a.name} (${a.assetId})'),
                                  overflow: TextOverflow.ellipsis,
                                  maxLines: 1,
                                ),
                              );
                            }).toList(),
                            onChanged: (id) {
                              if (id != null) {
                                setState(() {
                                  _selectedAsset =
                                      _assets.firstWhere((a) => a.assetId == id);
                                });
                              }
                            },
                          ),
                        ),
                      ),
                    ),

                  const Spacer(),

                  // Live IoT Pulse Indicator
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: isVeryCompact ? 4 : 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: CivilColors.healthy.withOpacity(0.12),
                      border: Border.all(color: CivilColors.healthy.withOpacity(0.4)),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: const BoxDecoration(
                            color: CivilColors.healthy,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Text(
                          isVeryCompact ? 'LIVE' : 'LIVE IOT',
                          style: const TextStyle(
                            color: CivilColors.healthy,
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(width: isVeryCompact ? 4 : 8),

                  // Theme Mode Selector
                  if (isVeryCompact)
                    InkWell(
                      onTap: () {
                        // Cycle theme mode: system -> dark -> light -> system
                        if (widget.themeNotifier.themeMode == ThemeMode.system) {
                          widget.themeNotifier.setThemeMode(ThemeMode.dark);
                        } else if (widget.themeNotifier.themeMode == ThemeMode.dark) {
                          widget.themeNotifier.setThemeMode(ThemeMode.light);
                        } else {
                          widget.themeNotifier.setThemeMode(ThemeMode.system);
                        }
                      },
                      child: Container(
                        padding: const EdgeInsets.all(5),
                        decoration: BoxDecoration(
                          border: Border.all(color: theme.colorScheme.outline),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Icon(
                          widget.themeNotifier.themeMode == ThemeMode.dark
                              ? Icons.dark_mode
                              : (widget.themeNotifier.themeMode == ThemeMode.light
                                  ? Icons.light_mode
                                  : Icons.brightness_auto),
                          size: 15,
                          color: CivilColors.steelBlue,
                        ),
                      ),
                    )
                  else
                    Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: theme.colorScheme.outline),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _ThemeModeButton(
                            icon: Icons.brightness_auto,
                            tooltip: 'System Device Theme',
                            isActive: widget.themeNotifier.themeMode == ThemeMode.system,
                            onTap: () => widget.themeNotifier.setThemeMode(ThemeMode.system),
                          ),
                          _ThemeModeButton(
                            icon: Icons.dark_mode,
                            tooltip: 'Dark Mode',
                            isActive: widget.themeNotifier.themeMode == ThemeMode.dark,
                            onTap: () => widget.themeNotifier.setThemeMode(ThemeMode.dark),
                          ),
                          _ThemeModeButton(
                            icon: Icons.light_mode,
                            tooltip: 'Light Mode',
                            isActive: widget.themeNotifier.themeMode == ThemeMode.light,
                            onTap: () => widget.themeNotifier.setThemeMode(ThemeMode.light),
                          ),
                        ],
                      ),
                    ),
                ],
              );
            },
          ),
        ),
      ),
      bottomNavigationBar: isMobile
          ? NavigationBar(
              selectedIndex: _currentTabIndex,
              onDestinationSelected: (idx) => setState(() => _currentTabIndex = idx),
              height: 58,
              labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
              destinations: destinations,
            )
          : null,
      body: isMobile
          ? mainContent
          : Row(
              children: [
                NavigationRail(
                  selectedIndex: _currentTabIndex,
                  onDestinationSelected: (idx) => setState(() => _currentTabIndex = idx),
                  labelType: NavigationRailLabelType.all,
                  backgroundColor: theme.appBarTheme.backgroundColor,
                  selectedIconTheme: IconThemeData(color: theme.colorScheme.primary),
                  selectedLabelTextStyle: TextStyle(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w700,
                    fontSize: 11,
                  ),
                  unselectedLabelTextStyle: theme.textTheme.bodySmall?.copyWith(fontSize: 11),
                  destinations: const [
                    NavigationRailDestination(
                      icon: Icon(Icons.dashboard_outlined),
                      selectedIcon: Icon(Icons.dashboard),
                      label: Text('SHM Live'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.photo_camera_outlined),
                      selectedIcon: Icon(Icons.photo_camera),
                      label: Text('Visual XAI'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.rule_folder_outlined),
                      selectedIcon: Icon(Icons.rule_folder),
                      label: Text('IDSS Decision'),
                    ),
                    NavigationRailDestination(
                      icon: Icon(Icons.account_balance_outlined),
                      selectedIcon: Icon(Icons.account_balance),
                      label: Text('Asset Registry'),
                    ),
                  ],
                ),
                VerticalDivider(thickness: 1, width: 1, color: theme.colorScheme.outline),
                Expanded(child: mainContent),
              ],
            ),
    );
  }
}

class _ThemeModeButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final bool isActive;
  final VoidCallback onTap;

  const _ThemeModeButton({
    required this.icon,
    required this.tooltip,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        color: isActive ? theme.colorScheme.primary.withOpacity(0.15) : null,
        child: Icon(
          icon,
          size: 15,
          color: isActive ? theme.colorScheme.primary : theme.colorScheme.onSurface.withOpacity(0.6),
        ),
      ),
    );
  }
}
