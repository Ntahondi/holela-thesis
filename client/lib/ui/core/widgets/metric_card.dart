import 'package:flutter/material.dart';
import '../theme.dart';

class TechnicalMetricCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final String? subtext;
  final String? channelId;
  final bool isAlert;

  const TechnicalMetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
    this.subtext,
    this.channelId,
    this.isAlert = false,
    // Kept for backward compatibility
    IconData? icon,
    Color accentColor = CivilColors.primary,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final borderColor = isAlert
        ? CivilColors.critical
        : (isDark ? CivilColors.darkBorder : CivilColors.lightBorder);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: isDark ? CivilColors.darkSurface : CivilColors.lightSurface,
        border: Border.all(
          color: borderColor,
          width: isAlert ? 1.5 : 1.0,
        ),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Header: Channel reference & Status dot
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                channelId ?? label.toUpperCase(),
                style: theme.textTheme.labelMedium?.copyWith(
                  fontSize: 10,
                  letterSpacing: 0.6,
                ),
                overflow: TextOverflow.ellipsis,
              ),
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  color: isAlert ? CivilColors.critical : CivilColors.healthy,
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),

          // Primary Numeric Value Display
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.baseline,
              textBaseline: TextBaseline.alphabetic,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    fontFamily: 'monospace',
                    letterSpacing: -0.5,
                    color: isAlert
                        ? CivilColors.critical
                        : (isDark ? CivilColors.darkTextPrimary : CivilColors.lightTextPrimary),
                  ),
                ),
                const SizedBox(width: 5),
                Text(
                  unit,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: isDark ? CivilColors.darkTextSecondary : CivilColors.lightTextSecondary,
                  ),
                ),
              ],
            ),
          ),

          // Subtext / Engineering Design Limit
          if (subtext != null)
            Text(
              subtext!,
              style: TextStyle(
                fontSize: 10,
                color: isAlert ? CivilColors.critical : (isDark ? CivilColors.darkTextMuted : CivilColors.lightTextMuted),
                fontFamily: 'monospace',
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
        ],
      ),
    );
  }
}
