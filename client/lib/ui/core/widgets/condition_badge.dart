import 'package:flutter/material.dart';
import '../theme.dart';

class ConditionBadge extends StatelessWidget {
  final int conditionIndex;
  final String conditionName;
  final double? confidencePct;
  final String? uncertaintyStr;
  final bool compact;

  const ConditionBadge({
    super.key,
    required this.conditionIndex,
    required this.conditionName,
    this.confidencePct,
    this.uncertaintyStr,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final color = CivilColors.getConditionColor(conditionIndex);
    final bg = CivilColors.getConditionBg(conditionIndex, isDark);

    if (compact) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: bg,
          border: Border.all(color: color.withOpacity(0.5)),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 4),
            Text(
              conditionName,
              style: TextStyle(
                color: color,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: color, width: 1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 6,
            runSpacing: 2,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(color: color, shape: BoxShape.circle),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    conditionName.toUpperCase(),
                    style: TextStyle(
                      color: color,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              if (confidencePct != null)
                Text(
                  '${confidencePct!.toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: color,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
            ],
          ),
          if (uncertaintyStr != null && uncertaintyStr!.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(
              uncertaintyStr!,
              style: TextStyle(
                color: color.withOpacity(0.85),
                fontSize: 10,
                fontFamily: 'monospace',
              ),
            ),
          ]
        ],
      ),
    );
  }
}
