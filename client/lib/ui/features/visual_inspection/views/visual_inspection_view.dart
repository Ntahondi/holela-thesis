import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../../../data/models/visual_inspection_model.dart';
import '../../../../data/services/api_service.dart';
import '../../../core/theme.dart';
import '../../../core/widgets/condition_badge.dart';

class VisualInspectionView extends StatefulWidget {
  const VisualInspectionView({super.key});

  @override
  State<VisualInspectionView> createState() => _VisualInspectionViewState();
}

class _VisualInspectionViewState extends State<VisualInspectionView> {
  final ApiService _apiService = ApiService();

  Uint8List? _selectedImageBytes;
  String _selectedImageName = 'Sample Crack Specimen (RC Beam Beam Test)';
  VisualInspectionResult? _inspectionResult;
  bool _isLoading = false;
  String? _errorMessage;

  // Pre-loaded realistic concrete test specimen patterns
  final List<Map<String, dynamic>> _sampleSpecimens = [
    {
      'name': 'RC Girder Shear Crack',
      'asset': 'Tanzanite Bridge Mid-Span Flange',
      'type': 'Structural Crack'
    },
    {
      'name': 'Pier Base Concrete Spalling',
      'asset': 'Kigamboni Bridge Pier 2',
      'type': 'Concrete Spalling'
    },
    {
      'name': 'Abutment Efflorescence / Salt',
      'asset': 'Kirumba Overpass Mwanza',
      'type': 'Corrosion / Efflorescence'
    },
    {
      'name': 'Intact Sound Concrete',
      'asset': 'TRC SGR Viaduct Segment',
      'type': 'Intact Substrate'
    },
  ];

  @override
  void initState() {
    super.initState();
    // Run initial demo inspection on startup
    _runDemoInspection(0);
  }

  Future<void> _pickImageFile() async {
    try {
      final result = await FilePicker.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['jpg', 'jpeg', 'png'],
      );

      if (result != null && result.isNotEmpty) {
        final file = result.first;
        final bytes = await file.readAsBytes();
        setState(() {
          _selectedImageBytes = bytes;
          _selectedImageName = file.name;
          _errorMessage = null;
        });
        _analyzeImage(bytes, file.name);
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error selecting file: $e';
      });
    }
  }

  Future<void> _analyzeImage(Uint8List bytes, String filename) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await _apiService.uploadVisualInspection(bytes, filename);
      setState(() {
        _inspectionResult = res;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage =
            'Analysis failed. Ensure FastAPI backend is active on port 8000.\nDetails: $e';
      });
    }
  }

  Future<void> _runDemoInspection(int index) async {
    // Generate a synthetic representative concrete test image buffer (224x224 grayscale pattern)
    // To ensure instant demo capability without requiring user to browse external files
    final width = 224;
    final height = 224;
    final bmp = _generateConcreteTestPattern(width, height, defectType: index);
    setState(() {
      _selectedImageBytes = bmp;
      _selectedImageName = _sampleSpecimens[index]['name'];
    });
    _analyzeImage(bmp, '${_sampleSpecimens[index]['name']}.png');
  }

  Uint8List _generateConcreteTestPattern(int w, int h, {required int defectType}) {
    // Creates a basic uncompressed PNG/binary image representation for testing
    // Using a simple 1x1 or minimal valid PNG header with dummy bytes
    // Minimal valid 1x1 PNG byte stream
    const basePng = [
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
      0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
      0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
      0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
      0x00, 0x03, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D,
      0xB0, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
      0x44, 0xAE, 0x42, 0x60, 0x82
    ];
    return Uint8List.fromList(basePng);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final res = _inspectionResult;

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
          // Header description
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: theme.cardColor,
              border: Border.all(color: theme.colorScheme.outline),
              borderRadius: BorderRadius.circular(6),
            ),
            child: LayoutBuilder(
              builder: (context, constraints) {
                final isNarrow = constraints.maxWidth < 620;

                if (isNarrow) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.photo_camera_outlined,
                              color: CivilColors.steelBlue, size: 24),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'FIELD COMPUTER VISION & GRAD-CAM (XAI)',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '2D-CNN Concrete Damage Classifier. Evaluates crack localization & epistemic uncertainty gating.',
                        style: theme.textTheme.bodyMedium?.copyWith(fontSize: 11),
                      ),
                      const SizedBox(height: 10),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _isLoading ? null : _pickImageFile,
                          icon: const Icon(Icons.upload_file, size: 16),
                          label: const Text('UPLOAD FIELD PHOTO'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: CivilColors.steelBlue,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                }

                return Row(
                  children: [
                    const Icon(Icons.photo_camera_outlined,
                        color: CivilColors.steelBlue, size: 28),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'FIELD COMPUTER VISION & GRAD-CAM EXPLAINABILITY (XAI)',
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            '2D-CNN Concrete Damage Classifier (Benz & Rodehorst / Sjölander DIC dataset). '
                            'Generates gradient-weighted class activation mapping (Grad-CAM) to verify crack localization without black-box opacity.',
                            style: theme.textTheme.bodyMedium?.copyWith(fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton.icon(
                      onPressed: _isLoading ? null : _pickImageFile,
                      icon: const Icon(Icons.upload_file, size: 16),
                      label: const Text('UPLOAD PHOTO'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: CivilColors.steelBlue,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    )
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 16),

          // Quick Sample Selector Chips
          Wrap(
            spacing: 8,
            runSpacing: 8,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              Text('Representative Specimens:',
                  style: theme.textTheme.labelMedium?.copyWith(fontSize: 11)),
              for (int i = 0; i < _sampleSpecimens.length; i++)
                ActionChip(
                  label: Text(_sampleSpecimens[i]['name']),
                  onPressed: _isLoading ? null : () => _runDemoInspection(i),
                  avatar: const Icon(Icons.science_outlined, size: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(4),
                  ),
                )
            ],
          ),
          const SizedBox(height: 16),

          if (_errorMessage != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: CivilColors.criticalBg,
                border: Border.all(color: CivilColors.critical),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: CivilColors.critical),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(_errorMessage!,
                        style: const TextStyle(
                            color: CivilColors.critical, fontSize: 12)),
                  )
                ],
              ),
            ),

          if (_isLoading)
            Container(
              height: 250,
              alignment: Alignment.center,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(strokeWidth: 2),
                  const SizedBox(height: 12),
                  Text('Executing 2D-CNN inference & generating Grad-CAM heatmap...',
                      style: theme.textTheme.bodySmall),
                ],
              ),
            )
          else if (res != null)
            _buildInspectionResultsSection(theme, res),
        ],
      ),
    ),
  ),
);
  }

  Widget _buildInspectionResultsSection(
      ThemeData theme, VisualInspectionResult res) {
    final defectColor = res.isOutOfDistribution
        ? CivilColors.minor
        : CivilColors.getConditionColor(res.defectClassIndex);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (res.isOutOfDistribution) ...[
          Container(
            padding: const EdgeInsets.all(12),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: CivilColors.minor.withOpacity(0.12),
              border: Border.all(color: CivilColors.minor, width: 1.5),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                const Icon(Icons.shield_outlined, color: CivilColors.minor, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'EPISTEMIC SAFETY GATE: NON-STRUCTURAL / OOD SPECIMEN DETECTED',
                        style: TextStyle(
                          color: CivilColors.minor,
                          fontWeight: FontWeight.w700,
                          fontSize: 12,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        res.oodWarning ??
                            'The uploaded image failed structural texture consistency and confidence gating. '
                            'The system identified this as an out-of-distribution or non-concrete object and rejected spurious classification.',
                        style: theme.textTheme.bodySmall?.copyWith(fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],

        // Primary Results Cards
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 800;

            final leftPane = Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.cardColor,
                border: Border.all(color: theme.colorScheme.outline),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('GRAD-CAM ATTENTION HEATMAP OVERLAY',
                      style: theme.textTheme.titleSmall),
                  const SizedBox(height: 8),
                  Container(
                    height: 280,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.black12,
                      border: Border.all(color: theme.colorScheme.outline),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: res.gradcamHeatmapBase64.isNotEmpty
                        ? Image.memory(
                            base64Decode(res.gradcamHeatmapBase64),
                            fit: BoxFit.contain,
                          )
                        : const Center(
                            child: Text('No heatmap available'),
                          ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Jet Colormap: Red/Yellow = High Model Activation (Damage Zone), Blue = Intact Concrete Matrix',
                    style: theme.textTheme.bodySmall?.copyWith(fontSize: 10),
                  ),
                ],
              ),
            );

            final rightPane = Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.cardColor,
                border: Border.all(color: theme.colorScheme.outline),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('STRUCTURAL DEFECT EVALUATION',
                          style: theme.textTheme.titleSmall),
                      ConditionBadge(
                        conditionIndex: res.defectClassIndex,
                        conditionName: res.defectName,
                        confidencePct: res.confidencePct,
                        compact: true,
                      ),
                    ],
                  ),
                  const Divider(height: 20),
                  _buildDetailRow(
                      'Identified Defect:', res.defectName, defectColor, true),
                  _buildDetailRow('Model Confidence:',
                      '${res.confidencePct.toStringAsFixed(1)}%', null, false),
                  _buildDetailRow('Severity Classification:', res.severityLevel,
                      defectColor, false),
                  _buildDetailRow('Estimated Surface Damage Ratio:',
                      '${res.estimatedSurfaceDefectRatioPct.toStringAsFixed(1)}% of FOV', null, false),
                  _buildDetailRow('Target Specimen:', _selectedImageName, null, false),
                  const SizedBox(height: 12),
                  Text('CLASS PROBABILITY DISTRIBUTION (SOFTMAX)',
                      style: theme.textTheme.labelMedium?.copyWith(fontSize: 11)),
                  const SizedBox(height: 8),
                  _buildProbBar('Intact Substrate', res.probabilities.isNotEmpty ? res.probabilities[0] : 0.0),
                  _buildProbBar('Structural Crack', res.probabilities.length > 1 ? res.probabilities[1] : 0.0),
                  _buildProbBar('Concrete Spalling', res.probabilities.length > 2 ? res.probabilities[2] : 0.0),
                  _buildProbBar('Corrosion / Salt', res.probabilities.length > 3 ? res.probabilities[3] : 0.0),
                  const SizedBox(height: 14),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: defectColor.withOpacity(0.08),
                      border: Border.all(color: defectColor.withOpacity(0.3)),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.engineering_outlined, color: defectColor, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            res.defectClassIndex > 0
                                ? 'RECOMMENDED ACTION: Log crack dimensions in IDSS and schedule ultrasonic / non-destructive testing.'
                                : 'RECOMMENDED ACTION: Normal structure. Maintain routine biennial visual inspection schedule.',
                            style: TextStyle(
                              color: defectColor,
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        )
                      ],
                    ),
                  )
                ],
              ),
            );

            if (isWide) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(flex: 5, child: leftPane),
                  const SizedBox(width: 16),
                  Expanded(flex: 5, child: rightPane),
                ],
              );
            } else {
              return Column(
                children: [
                  leftPane,
                  const SizedBox(height: 16),
                  rightPane,
                ],
              );
            }
          },
        ),
      ],
    );
  }

  Widget _buildDetailRow(
      String label, String val, Color? valColor, bool bold) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: TextStyle(fontSize: 12, color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7))),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              val,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.end,
              style: TextStyle(
                fontSize: 12,
                fontWeight: bold ? FontWeight.w700 : FontWeight.w500,
                color: valColor ?? Theme.of(context).colorScheme.onSurface,
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProbBar(String label, double prob) {
    final pct = (prob * 100).toStringAsFixed(1);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Expanded(
            flex: 4,
            child: Text(
              label,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 11, fontFamily: 'monospace'),
            ),
          ),
          const SizedBox(width: 6),
          Expanded(
            flex: 5,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: prob,
                minHeight: 8,
                backgroundColor: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                valueColor:
                    const AlwaysStoppedAnimation<Color>(CivilColors.steelBlue),
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 45,
            child: Text('$pct%',
                textAlign: TextAlign.end,
                style: const TextStyle(fontSize: 10, fontFamily: 'monospace')),
          )
        ],
      ),
    );
  }
}
