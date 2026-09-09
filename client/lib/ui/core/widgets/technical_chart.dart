import 'dart:math';
import 'package:flutter/material.dart';
import '../theme.dart';

class EngineeringDataPoint {
  final double value;
  final double? secondaryValue;
  final String timestamp;

  EngineeringDataPoint({
    required this.value,
    this.secondaryValue,
    required this.timestamp,
  });
}

class TechnicalEngineeringChart extends StatelessWidget {
  final String title;
  final String primaryUnit;
  final String? secondaryUnit;
  final List<EngineeringDataPoint> dataPoints;
  final double? criticalThreshold;
  final double? warningThreshold;
  final Color primaryColor;
  final Color secondaryColor;
  final double height;

  const TechnicalEngineeringChart({
    super.key,
    required this.title,
    required this.primaryUnit,
    this.secondaryUnit,
    required this.dataPoints,
    this.criticalThreshold,
    this.warningThreshold,
    this.primaryColor = CivilColors.seriesPrimary,
    this.secondaryColor = CivilColors.seriesSecondary,
    this.height = 200,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textTheme = Theme.of(context).textTheme;

    return Container(
      height: height,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        border: Border.all(color: Theme.of(context).colorScheme.outline),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 3,
                height: 14,
                color: primaryColor,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: textTheme.titleSmall?.copyWith(fontSize: 11),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              _LegendChip(
                label: primaryUnit,
                color: primaryColor,
                isDashed: false,
              ),
              if (secondaryUnit != null)
                _LegendChip(
                  label: secondaryUnit!,
                  color: secondaryColor,
                  isDashed: false,
                ),
              if (criticalThreshold != null)
                _LegendChip(
                  label: 'Threshold (${criticalThreshold!.toStringAsFixed(0)})',
                  color: CivilColors.critical,
                  isDashed: true,
                ),
            ],
          ),
          const SizedBox(height: 8),
          Expanded(
            child: dataPoints.isEmpty
                ? Center(
                    child: Text('Awaiting telemetry...',
                        style: textTheme.bodySmall))
                : CustomPaint(
                    size: Size.infinite,
                    painter: _EngineeringChartPainter(
                      dataPoints: dataPoints,
                      primaryColor: primaryColor,
                      secondaryColor: secondaryColor,
                      criticalThreshold: criticalThreshold,
                      warningThreshold: warningThreshold,
                      isDark: isDark,
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

class _LegendChip extends StatelessWidget {
  final String label;
  final Color color;
  final bool isDashed;

  const _LegendChip({
    required this.label,
    required this.color,
    required this.isDashed,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 2,
          color: color,
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: color,
            fontWeight: FontWeight.w600,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }
}

class _EngineeringChartPainter extends CustomPainter {
  final List<EngineeringDataPoint> dataPoints;
  final Color primaryColor;
  final Color secondaryColor;
  final double? criticalThreshold;
  final double? warningThreshold;
  final bool isDark;

  _EngineeringChartPainter({
    required this.dataPoints,
    required this.primaryColor,
    required this.secondaryColor,
    this.criticalThreshold,
    this.warningThreshold,
    required this.isDark,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (dataPoints.isEmpty) return;

    final gridPaint = Paint()
      ..color = (isDark ? Colors.white : Colors.black).withOpacity(0.08)
      ..strokeWidth = 1.0;

    // Draw horizontal grid lines
    const int gridDivs = 4;
    for (int i = 0; i <= gridDivs; i++) {
      final y = size.height * (i / gridDivs);
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }

    // Min and Max calculation
    double minVal = dataPoints.map((p) => p.value).reduce(min);
    double maxVal = dataPoints.map((p) => p.value).reduce(max);
    if (criticalThreshold != null) {
      maxVal = max(maxVal, criticalThreshold! * 1.05);
      minVal = min(minVal, criticalThreshold! * 0.7);
    }
    if (maxVal == minVal) {
      maxVal += 1.0;
      minVal -= 1.0;
    }
    final range = maxVal - minVal;

    // Plot Critical Threshold line if present
    if (criticalThreshold != null) {
      final threshY =
          size.height - ((criticalThreshold! - minVal) / range) * size.height;
      final threshPaint = Paint()
        ..color = CivilColors.critical
        ..strokeWidth = 1.2
        ..style = PaintingStyle.stroke;

      // Draw dashed line
      double startX = 0;
      while (startX < size.width) {
        canvas.drawLine(
          Offset(startX, threshY),
          Offset(min(startX + 6, size.width), threshY),
          threshPaint,
        );
        startX += 10;
      }
    }

    // Plot Primary Data Line
    final linePaint = Paint()
      ..color = primaryColor
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    final stepX = size.width / max(1, dataPoints.length - 1);

    for (int i = 0; i < dataPoints.length; i++) {
      final x = i * stepX;
      final normY = (dataPoints[i].value - minVal) / range;
      final y = size.height - (normY * size.height);

      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    canvas.drawPath(path, linePaint);

    // Subtle area fill under primary curve
    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          primaryColor.withOpacity(0.18),
          primaryColor.withOpacity(0.0),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.fill;

    final fillPath = Path.from(path)
      ..lineTo((dataPoints.length - 1) * stepX, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(fillPath, fillPaint);

    // Latest Value Indicator Node
    if (dataPoints.isNotEmpty) {
      final lastIdx = dataPoints.length - 1;
      final lastX = lastIdx * stepX;
      final lastNormY = (dataPoints[lastIdx].value - minVal) / range;
      final lastY = size.height - (lastNormY * size.height);

      canvas.drawCircle(
          Offset(lastX, lastY), 4, Paint()..color = primaryColor);
      canvas.drawCircle(
        Offset(lastX, lastY),
        2,
        Paint()..color = isDark ? const Color(0xFF0F172A) : Colors.white,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _EngineeringChartPainter oldDelegate) => true;
}
